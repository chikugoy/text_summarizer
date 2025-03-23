from datetime import datetime
from typing import List, Optional, UUID
from pydantic import BaseModel, Field


# リクエスト用スキーマ
class SummaryCreate(BaseModel):
    """要約作成リクエスト"""
    title: str = Field(..., min_length=1, max_length=255, description="要約のタイトル")
    description: Optional[str] = Field(None, description="要約の説明（オプション）")
    original_text: str = Field(..., min_length=1, description="要約元のテキスト")
    summarized_text: str = Field(..., min_length=1, description="要約されたテキスト")


class SummaryUpdate(BaseModel):
    """要約更新リクエスト"""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="要約のタイトル")
    description: Optional[str] = Field(None, description="要約の説明")


# レスポンス用スキーマ
class SummaryBase(BaseModel):
    """要約の基本情報"""
    id: UUID
    title: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class SummaryDetail(SummaryBase):
    """要約の詳細情報"""
    original_text: str
    summarized_text: str

    class Config:
        orm_mode = True


class SummaryList(BaseModel):
    """要約一覧レスポンス"""
    items: List[SummaryBase]
    total: int
    page: int
    page_size: int
    
    class Config:
        orm_mode = True
