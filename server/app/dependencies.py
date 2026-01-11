"""依存性注入のための依存関係定義

FastAPIの依存性注入システムで使用するファクトリ関数とバリデータ。
"""

from functools import lru_cache
from typing import Generator

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db


# ============================================
# サービスファクトリ関数
# ============================================


@lru_cache()
def get_summary_service():
    """SummaryServiceのインスタンスを取得する

    キャッシュされたシングルトンインスタンスを返す。
    """
    from app.services.summary_service import SummaryService

    return SummaryService()


@lru_cache()
def get_ocr_service():
    """OCRサービスのインスタンスを取得する

    設定に基づいてGoogle VisionまたはPaddleOCRを選択。
    """
    from app.services.ocr_service import get_ocr_service as create_ocr_service

    return create_ocr_service()


@lru_cache()
def get_file_service():
    """FileServiceのインスタンスを取得する"""
    from app.services.file_service import FileService

    return FileService()


# ============================================
# バリデータ
# ============================================


def verify_upload_size(file_size: int):
    """アップロードファイルのサイズを検証する

    Args:
        file_size: ファイルサイズ（バイト）

    Raises:
        HTTPException: ファイルサイズが上限を超えている場合
    """
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"ファイルサイズが大きすぎます。最大サイズは {settings.MAX_UPLOAD_SIZE / (1024 * 1024):.1f}MB です。",
        )
    return True
