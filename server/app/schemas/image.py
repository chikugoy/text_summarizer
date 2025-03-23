from datetime import datetime
from typing import List, Optional, UUID
from pydantic import BaseModel, Field


# リクエスト用スキーマ
class ImageCreate(BaseModel):
    """画像作成リクエスト（内部使用）"""
    summary_id: UUID
    file_path: str
    file_name: str
    file_size: int
    mime_type: str
    ocr_text: Optional[str] = None
    page_number: int


# レスポンス用スキーマ
class ImageBase(BaseModel):
    """画像の基本情報"""
    id: UUID
    file_name: str
    file_size: int
    mime_type: str
    page_number: int
    created_at: datetime

    class Config:
        orm_mode = True


class ImageDetail(ImageBase):
    """画像の詳細情報"""
    file_path: str
    ocr_text: Optional[str] = None
    summary_id: UUID

    class Config:
        orm_mode = True


class ImageList(BaseModel):
    """画像一覧レスポンス"""
    items: List[ImageBase]
    total: int
    
    class Config:
        orm_mode = True


# OCR処理関連スキーマ
class OCRRequest(BaseModel):
    """OCR処理リクエスト"""
    image_ids: List[UUID] = Field(..., description="OCR処理を行う画像IDのリスト")


class OCRResult(BaseModel):
    """OCR処理結果"""
    image_id: UUID
    ocr_text: str
    success: bool
    error: Optional[str] = None


class OCRResponse(BaseModel):
    """OCR処理レスポンス"""
    results: List[OCRResult]
    job_id: str
    status: str
