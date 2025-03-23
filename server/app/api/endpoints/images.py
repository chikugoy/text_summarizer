from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
import uuid

from app.database import get_db
from app.dependencies import verify_upload_size
from app.models import Image, Summary
from app.schemas import ImageList, ImageDetail, ImageBase
from app.services import file_service

router = APIRouter()


@router.post("/upload", response_model=List[ImageBase], status_code=status.HTTP_201_CREATED)
async def upload_images(
    files: List[UploadFile] = File(...),
    summary_id: uuid.UUID = None,
    db: Session = Depends(get_db)
):
    """複数の書籍ページ画像をアップロードする"""
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ファイルがアップロードされていません"
        )
    
    # サマリーIDが指定されている場合、存在確認
    if summary_id:
        summary = db.query(Summary).filter(Summary.id == summary_id).first()
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID {summary_id} の要約が見つかりません"
            )
    
    # 一時的なサマリーを作成（サマリーIDが指定されていない場合）
    if not summary_id:
        new_summary = Summary(
            title="一時的な要約",
            description="画像アップロード用の一時的な要約",
            original_text="",
            summarized_text=""
        )
        db.add(new_summary)
        db.commit()
        db.refresh(new_summary)
        summary_id = new_summary.id
    
    # ファイルサイズの検証
    for file in files:
        await file.seek(0)  # ファイルポインタをリセット
        content = await file.read()
        await file.seek(0)  # ファイルポインタを再度リセット
        verify_upload_size(len(content))
    
    # ファイルの保存
    saved_files = await file_service.save_multiple_files(files, str(summary_id))
    
    # データベースに画像情報を保存
    db_images = []
    for file_info in saved_files:
        db_image = Image(
            summary_id=summary_id,
            file_path=file_info["file_path"],
            file_name=file_info["file_name"],
            file_size=file_info["file_size"],
            mime_type=file_info["mime_type"],
            page_number=file_info["page_number"]
        )
        db.add(db_image)
        db_images.append(db_image)
    
    db.commit()
    for image in db_images:
        db.refresh(image)
    
    return db_images


@router.get("/{summary_id}", response_model=ImageList)
def get_images_by_summary(
    summary_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """特定の要約に関連する画像一覧を取得する"""
    # サマリーの存在確認
    summary = db.query(Summary).filter(Summary.id == summary_id).first()
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {summary_id} の要約が見つかりません"
        )
    
    # 画像の取得
    images = db.query(Image).filter(Image.summary_id == summary_id).order_by(Image.page_number).all()
    
    return {
        "items": images,
        "total": len(images)
    }


@router.get("/{image_id}/detail", response_model=ImageDetail)
def get_image_detail(
    image_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """特定の画像の詳細情報を取得する"""
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {image_id} の画像が見つかりません"
        )
    
    return image


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_image(
    image_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """画像を削除する"""
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {image_id} の画像が見つかりません"
        )
    
    # ファイルの削除
    file_service.delete_file(image.file_path)
    
    # データベースから削除
    db.delete(image)
    db.commit()
    
    return None
