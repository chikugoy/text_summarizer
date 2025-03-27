from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
import uuid
import logging
import sys
from datetime import datetime

from app.database import get_db
from app.models import Summary, Image
from app.schemas import SummaryCreate, SummaryUpdate, SummaryBase, SummaryDetail, SummaryList, SummaryGenerate
from app.services import summary_service, ocr_service

# ロガーの設定
logger = logging.getLogger(__name__)

# 直接標準エラー出力にメッセージを出力（デバッグ用）
print("summaries.py モジュールがロードされました", file=sys.stderr)
sys.stderr.flush()

router = APIRouter()


@router.post("", response_model=SummaryDetail, status_code=status.HTTP_201_CREATED)
def create_summary(
    summary: SummaryCreate,
    db: Session = Depends(get_db)
):
    """OCR処理された文章から要約を生成して保存する"""
    logger.info("要約の新規作成開始")
    
    # 要約の作成
    db_summary = Summary(
        title=summary.title,
        description=summary.description,
        original_text=summary.original_text,
        summarized_text=summary.summarized_text
    )
    
    try:
        db.add(db_summary)
        db.commit()
        db.refresh(db_summary)
        logger.info(f"要約の新規作成完了: id={db_summary.id}")
    except Exception as e:
        logger.error(f"要約の新規作成中にエラーが発生しました: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"要約の新規作成中にエラーが発生しました: {str(e)}"
        )
    
    return db_summary

@router.post("/generate", response_model=SummaryDetail)
def generate_summary(
    request: SummaryGenerate,
    db: Session = Depends(get_db)
):
    """特定の要約IDに関連する画像からOCRテキストを抽出し、要約を生成する"""
    try:
        # 直接標準エラー出力にメッセージを出力（デバッグ用）
        print(f"generate_summary が呼び出されました: summary_id={request.summary_id}, type={type(request.summary_id)}", file=sys.stderr)
        sys.stderr.flush()
        
        # リクエストの内容を詳細に出力
        print(f"リクエスト内容: {request}", file=sys.stderr)
        print(f"リクエスト内容（dict）: {request.model_dump()}", file=sys.stderr)
        sys.stderr.flush()
        
        logger.info(f"要約生成開始: summary_id={request.summary_id}")
        
        summary_id = request.summary_id
        print(f"summary_id変数: {summary_id}, type={type(summary_id)}", file=sys.stderr)
        sys.stderr.flush()
    except Exception as e:
        error_msg = f"リクエスト処理中にエラーが発生しました: {str(e)}"
        print(error_msg, file=sys.stderr)
        sys.stderr.flush()
        logger.error(error_msg, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )
    
    try:
        # 要約の存在確認
        logger.debug(f"要約の存在確認: summary_id={summary_id}")
        print(f"要約の存在確認: summary_id={summary_id}, 型={type(summary_id)}", file=sys.stderr)
        sys.stderr.flush()
        
        summary = db.query(Summary).filter(Summary.id == summary_id).first()
        if not summary:
            logger.warning(f"要約が見つかりません: summary_id={summary_id}")
            print(f"要約が見つかりません: summary_id={summary_id}", file=sys.stderr)
            sys.stderr.flush()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID {summary_id} の要約が見つかりません"
            )
        
        print(f"要約が見つかりました: summary={summary.id}", file=sys.stderr)
        sys.stderr.flush()
        
        # 関連する画像の取得
        logger.debug(f"関連画像の取得: summary_id={summary_id}")
        images = db.query(Image).filter(Image.summary_id == summary_id).order_by(Image.page_number).all()
        if not images:
            logger.warning(f"関連画像がありません: summary_id={summary_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="この要約に関連する画像がありません"
            )
        
        print(f"関連画像が見つかりました: 画像数={len(images)}", file=sys.stderr)
        sys.stderr.flush()
        
        # OCRテキストの結合
        logger.debug(f"OCRテキストの結合: 画像数={len(images)}")
        original_text = ""
        for image in images:
            if image.ocr_text:
                original_text += image.ocr_text + "\n\n"
        
        if not original_text:
            logger.warning("OCRテキストが抽出されていません")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OCRテキストが抽出されていません。先にOCR処理を実行してください。"
            )
        
        print(f"OCRテキストの結合完了: 文字数={len(original_text)}", file=sys.stderr)
        sys.stderr.flush()
        
        # 要約の生成
        logger.debug("要約の生成開始")
        try:
            summarized_text = summary_service.summarize_text(original_text)
            logger.debug(f"要約の生成完了: 文字数={len(summarized_text)}")
            print(f"要約の生成完了: 文字数={len(summarized_text)}", file=sys.stderr)
            sys.stderr.flush()
        except Exception as e:
            error_msg = f"要約の生成中にエラーが発生しました: {str(e)}"
            logger.error(error_msg, exc_info=True)
            print(error_msg, file=sys.stderr)
            sys.stderr.flush()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg
            )
        
        # 要約の更新
        logger.debug("要約情報の更新")
        summary.original_text = original_text
        
        # summarized_textが文字列か確認
        if not isinstance(summarized_text, str):
            logger.warning(f"要約テキストが文字列ではありません: type={type(summarized_text)}")
            summarized_text = str(summarized_text)
        
        summary.summarized_text = summarized_text
        
        try:
            db.commit()
            db.refresh(summary)
            logger.info(f"要約生成完了: summary_id={summary_id}")
            print(f"要約生成完了: summary_id={summary_id}", file=sys.stderr)
            sys.stderr.flush()
        except Exception as e:
            error_msg = f"データベース更新中にエラーが発生しました: {str(e)}"
            logger.error(error_msg, exc_info=True)
            print(error_msg, file=sys.stderr)
            sys.stderr.flush()
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg
            )
        
        return summary
    except Exception as e:
        if not isinstance(e, HTTPException):
            error_msg = f"予期せぬエラーが発生しました: {str(e)}"
            logger.error(error_msg, exc_info=True)
            print(error_msg, file=sys.stderr)
            sys.stderr.flush()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg
            )
        raise


@router.get("", response_model=SummaryList)
def get_summaries(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """要約一覧を取得する（ページネーション付き）"""
    # 説明(description)がNULLでなく、かつタイトルが「一時的な要約」でない要約のみ取得
    # 大文字小文字を区別しない比較のためにlower()を使用
    total = db.query(Summary).filter(
        Summary.description.isnot(None),
        func.lower(Summary.title) != "一時的な要約"
    ).count()
    summaries = db.query(Summary).filter(
        Summary.description.isnot(None),
        func.lower(Summary.title) != "一時的な要約"
    ) \
        .order_by(Summary.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "items": summaries,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "page_size": limit
    }


@router.get("/{summary_id}", response_model=SummaryDetail)
def get_summary(
    summary_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """特定の要約詳細を取得する"""
    summary = db.query(Summary).filter(Summary.id == summary_id).first()
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {summary_id} の要約が見つかりません"
        )
    
    return summary


@router.put("/{summary_id}", response_model=SummaryDetail)
def update_summary(
    summary_id: uuid.UUID,
    summary_update: SummaryUpdate,
    db: Session = Depends(get_db)
):
    """既存の要約情報を更新する（タイトル、説明など）"""
    summary = db.query(Summary).filter(Summary.id == summary_id).first()
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {summary_id} の要約が見つかりません"
        )
    
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
    db: Session = Depends(get_db)
):
    """要約を削除する"""
    summary = db.query(Summary).filter(Summary.id == summary_id).first()
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {summary_id} の要約が見つかりません"
        )
    
    # 関連する画像も削除される（cascade="all, delete-orphan"の設定による）
    db.delete(summary)
    db.commit()
    
    return None
