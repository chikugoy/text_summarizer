"""要約APIエンドポイントモジュール

要約の作成、取得、更新、削除のAPIエンドポイントを提供する。
"""

import logging
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Summary, Image
from app.schemas import (
    SummaryCreate,
    SummaryUpdate,
    SummaryBase,
    SummaryDetail,
    SummaryList,
    SummaryGenerate,
)
from app.services import summary_service
from app.utils import get_or_404, SummaryConstants

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("", response_model=SummaryDetail, status_code=status.HTTP_201_CREATED)
def create_summary(
    summary: SummaryCreate,
    db: Session = Depends(get_db),
) -> Summary:
    """要約を新規作成する

    Args:
        summary: 要約作成リクエスト
        db: データベースセッション

    Returns:
        作成された要約
    """
    logger.info("要約の新規作成開始")

    db_summary = Summary(
        title=summary.title,
        description=summary.description,
        original_text=summary.original_text,
        summarized_text=summary.summarized_text,
    )

    try:
        db.add(db_summary)
        db.commit()
        db.refresh(db_summary)
        logger.info(f"要約の新規作成完了: id={db_summary.id}")
        return db_summary
    except Exception as e:
        logger.error(f"要約の新規作成エラー: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"要約の作成中にエラーが発生しました: {e}",
        )


@router.post("/generate", response_model=SummaryDetail)
def generate_summary(
    request: SummaryGenerate,
    db: Session = Depends(get_db),
) -> Summary:
    """画像からOCRテキストを抽出し、要約を生成する

    Args:
        request: 要約生成リクエスト（summary_idとcustom_instructionsを含む）
        db: データベースセッション

    Returns:
        生成された要約
    """
    summary_id = request.summary_id
    custom_instructions = request.custom_instructions
    logger.info(f"要約生成開始: summary_id={summary_id}")

    # 要約の存在確認
    summary = get_or_404(db, Summary, summary_id, "要約")

    # 関連する画像の取得
    images = (
        db.query(Image)
        .filter(Image.summary_id == summary_id)
        .order_by(Image.page_number)
        .all()
    )

    if not images:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="この要約に関連する画像がありません",
        )

    # OCRテキストの結合
    original_text = _combine_ocr_texts(images)

    if not original_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OCRテキストが抽出されていません。先にOCR処理を実行してください。",
        )

    # 要約の生成
    try:
        summarized_text = summary_service.summarize_text(
            original_text,
            custom_instructions=custom_instructions,
        )
    except Exception as e:
        logger.error(f"要約生成エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"要約の生成中にエラーが発生しました: {e}",
        )

    # 要約の更新
    summary.original_text = original_text
    summary.summarized_text = str(summarized_text)
    summary.custom_instructions = custom_instructions

    try:
        db.commit()
        db.refresh(summary)
        logger.info(f"要約生成完了: summary_id={summary_id}")
        return summary
    except Exception as e:
        logger.error(f"データベース更新エラー: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"データベース更新中にエラーが発生しました: {e}",
        )


@router.get("", response_model=SummaryList)
def get_summaries(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
) -> dict:
    """要約一覧を取得する（ページネーション付き）

    一時的な要約は除外される。

    Args:
        skip: スキップする件数
        limit: 取得する最大件数
        db: データベースセッション

    Returns:
        要約一覧とページネーション情報
    """
    # 一時的な要約を除外するフィルタ
    base_query = db.query(Summary).filter(
        Summary.description.isnot(None),
        func.lower(Summary.title) != SummaryConstants.TEMPORARY_TITLE.lower(),
    )

    total = base_query.count()
    summaries = (
        base_query.order_by(Summary.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return {
        "items": summaries,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "page_size": limit,
    }


@router.get("/{summary_id}", response_model=SummaryDetail)
def get_summary(
    summary_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> Summary:
    """特定の要約詳細を取得する

    Args:
        summary_id: 要約ID
        db: データベースセッション

    Returns:
        要約詳細
    """
    return get_or_404(db, Summary, summary_id, "要約")


@router.put("/{summary_id}", response_model=SummaryDetail)
def update_summary(
    summary_id: uuid.UUID,
    summary_update: SummaryUpdate,
    db: Session = Depends(get_db),
) -> Summary:
    """要約情報を更新する

    Args:
        summary_id: 要約ID
        summary_update: 更新内容
        db: データベースセッション

    Returns:
        更新された要約
    """
    summary = get_or_404(db, Summary, summary_id, "要約")

    # 更新するフィールドを設定
    if summary_update.title is not None:
        summary.title = summary_update.title
    if summary_update.description is not None:
        summary.description = summary_update.description

    db.commit()
    db.refresh(summary)

    return summary


@router.delete("/{summary_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_summary(
    summary_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> None:
    """要約を削除する

    関連する画像も自動的に削除される。

    Args:
        summary_id: 要約ID
        db: データベースセッション
    """
    summary = get_or_404(db, Summary, summary_id, "要約")

    db.delete(summary)
    db.commit()


def _combine_ocr_texts(images: list) -> str:
    """画像のOCRテキストを結合する

    Args:
        images: 画像のリスト

    Returns:
        結合されたOCRテキスト
    """
    texts = [image.ocr_text for image in images if image.ocr_text]
    return "\n\n".join(texts)
