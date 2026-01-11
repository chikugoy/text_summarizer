"""画像APIエンドポイントモジュール

画像のアップロード、取得、削除のAPIエンドポイントを提供する。
"""

import logging
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import verify_upload_size
from app.models import Image, Summary
from app.schemas import ImageList, ImageDetail, ImageBase
from app.services import file_service
from app.utils import get_or_404, get_optional, SummaryConstants

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload", response_model=List[ImageBase], status_code=status.HTTP_201_CREATED)
async def upload_images(
    files: List[UploadFile] = File(...),
    summary_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db),
) -> List[Image]:
    """複数の書籍ページ画像をアップロードする

    Args:
        files: アップロードするファイルのリスト
        summary_id: 関連付ける要約ID（省略時は一時的な要約を作成）
        db: データベースセッション

    Returns:
        アップロードされた画像情報のリスト
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ファイルがアップロードされていません",
        )

    # サマリーIDが指定されている場合、存在確認
    if summary_id:
        get_or_404(db, Summary, summary_id, "要約")
    else:
        # 一時的なサマリーを作成
        summary_id = _create_temporary_summary(db)

    # ファイルサイズの検証
    await _validate_file_sizes(files)

    # ファイルの保存
    saved_files = await file_service.save_multiple_files(files, str(summary_id))

    # データベースに画像情報を保存
    db_images = _save_images_to_db(db, summary_id, saved_files)

    logger.info(f"画像アップロード完了: {len(db_images)}件, summary_id={summary_id}")
    return db_images


@router.get("/{summary_id}", response_model=ImageList)
def get_images_by_summary(
    summary_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> dict:
    """特定の要約に関連する画像一覧を取得する

    Args:
        summary_id: 要約ID
        db: データベースセッション

    Returns:
        画像一覧とトータル件数
    """
    get_or_404(db, Summary, summary_id, "要約")

    images = (
        db.query(Image)
        .filter(Image.summary_id == summary_id)
        .order_by(Image.page_number)
        .all()
    )

    return {"items": images, "total": len(images)}


@router.get("/{image_id}/detail", response_model=ImageDetail)
def get_image_detail(
    image_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> Image:
    """特定の画像の詳細情報を取得する

    Args:
        image_id: 画像ID
        db: データベースセッション

    Returns:
        画像詳細情報
    """
    return get_or_404(db, Image, image_id, "画像")


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_image(
    image_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> None:
    """画像を削除する

    Args:
        image_id: 画像ID
        db: データベースセッション
    """
    image = get_or_404(db, Image, image_id, "画像")

    # ファイルの削除
    file_service.delete_file(image.file_path)

    # データベースから削除
    db.delete(image)
    db.commit()

    logger.info(f"画像削除完了: image_id={image_id}")


def _create_temporary_summary(db: Session) -> uuid.UUID:
    """一時的な要約を作成する

    Args:
        db: データベースセッション

    Returns:
        作成された要約のID
    """
    new_summary = Summary(
        title=SummaryConstants.TEMPORARY_TITLE,
        description=SummaryConstants.TEMPORARY_DESCRIPTION,
        original_text="",
        summarized_text="",
    )
    db.add(new_summary)
    db.commit()
    db.refresh(new_summary)
    return new_summary.id


async def _validate_file_sizes(files: List[UploadFile]) -> None:
    """ファイルサイズを検証する

    Args:
        files: 検証するファイルのリスト

    Raises:
        HTTPException: ファイルサイズが上限を超えている場合
    """
    for file in files:
        await file.seek(0)
        content = await file.read()
        await file.seek(0)
        verify_upload_size(len(content))


def _save_images_to_db(
    db: Session,
    summary_id: uuid.UUID,
    saved_files: List[dict],
) -> List[Image]:
    """画像情報をデータベースに保存する

    Args:
        db: データベースセッション
        summary_id: 要約ID
        saved_files: 保存されたファイル情報のリスト

    Returns:
        保存された画像オブジェクトのリスト
    """
    db_images = []
    for file_info in saved_files:
        db_image = Image(
            summary_id=summary_id,
            file_path=file_info["file_path"],
            file_name=file_info["file_name"],
            file_size=file_info["file_size"],
            mime_type=file_info["mime_type"],
            page_number=file_info["page_number"],
        )
        db.add(db_image)
        db_images.append(db_image)

    db.commit()
    for image in db_images:
        db.refresh(image)

    return db_images
