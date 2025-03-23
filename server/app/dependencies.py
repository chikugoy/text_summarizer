from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings


# 共通の依存関係をここに定義
# 例: 認証、レート制限、アクセス制御など

def verify_upload_size(file_size: int):
    """アップロードファイルのサイズを検証する"""
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"ファイルサイズが大きすぎます。最大サイズは {settings.MAX_UPLOAD_SIZE / (1024 * 1024):.1f}MB です。"
        )
    return True


# 他の共通依存関係を必要に応じて追加
