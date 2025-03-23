from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from app.database import get_db
from app.models import Image
from app.schemas import OCRRequest, OCRResponse
from app.services import ocr_service

router = APIRouter()


@router.post("/process", response_model=OCRResponse)
def process_ocr(
    request: OCRRequest,
    db: Session = Depends(get_db)
):
    """アップロードされた画像のOCR処理を実行する"""
    # 画像の存在確認
    images = []
    for image_id in request.image_ids:
        image = db.query(Image).filter(Image.id == image_id).first()
        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID {image_id} の画像が見つかりません"
            )
        images.append(image)
    
    # OCR処理の実行
    job_id = ocr_service.process_images(images)
    
    # 処理結果の取得
    job_status = ocr_service.get_job_status(job_id)
    
    # OCR結果をデータベースに保存
    for result in job_status["results"]:
        if result["success"]:
            image_id = result["image_id"]
            ocr_text = result["ocr_text"]
            
            # 画像のOCRテキストを更新
            image = db.query(Image).filter(Image.id == image_id).first()
            if image:
                image.ocr_text = ocr_text
    
    db.commit()
    
    return {
        "results": job_status["results"],
        "job_id": job_id,
        "status": job_status["status"]
    }


@router.get("/status/{job_id}", response_model=OCRResponse)
def get_ocr_status(
    job_id: str,
    db: Session = Depends(get_db)
):
    """OCR処理のステータスを確認する"""
    job_status = ocr_service.get_job_status(job_id)
    if not job_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ジョブID {job_id} が見つかりません"
        )
    
    return {
        "results": job_status["results"],
        "job_id": job_id,
        "status": job_status["status"]
    }
