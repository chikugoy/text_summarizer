"""データベースヘルパー関数モジュール

共通のデータベース操作を提供する。
"""

from typing import Type, TypeVar, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.database import Base

# ジェネリック型変数
T = TypeVar("T", bound=Base)


def get_or_404(
    db: Session,
    model: Type[T],
    resource_id: UUID,
    resource_name: str = "リソース",
) -> T:
    """リソースを取得し、存在しない場合は404エラーを発生させる

    Args:
        db: データベースセッション
        model: SQLAlchemyモデルクラス
        resource_id: リソースのID
        resource_name: エラーメッセージに表示するリソース名

    Returns:
        取得したリソース

    Raises:
        HTTPException: リソースが存在しない場合（404）
    """
    resource = db.query(model).filter(model.id == resource_id).first()
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {resource_id} の{resource_name}が見つかりません",
        )
    return resource


def get_optional(
    db: Session,
    model: Type[T],
    resource_id: UUID,
) -> Optional[T]:
    """リソースを取得する（存在しない場合はNone）

    Args:
        db: データベースセッション
        model: SQLAlchemyモデルクラス
        resource_id: リソースのID

    Returns:
        取得したリソース、存在しない場合はNone
    """
    return db.query(model).filter(model.id == resource_id).first()
