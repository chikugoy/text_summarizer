from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

# データベースエンジンを作成
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

# セッションファクトリを作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# モデルのベースクラスを作成
Base = declarative_base()


# 依存性注入用のデータベースセッション取得関数
def get_db():
    """リクエストごとにデータベースセッションを取得し、終了時に閉じる"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
