import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.api import api_router
from app.config import settings
from app.database import engine, Base

# データベースの初期化
Base.metadata.create_all(bind=engine)

# FastAPIアプリケーションの作成
app = FastAPI(
    title=settings.APP_NAME,
    description="書籍画像要約サービス - 複数の書籍ページ画像をアップロードすると要約してくれるウェブアプリケーション",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に制限する
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# APIルーターの登録
app.include_router(api_router, prefix="/api")

# アップロードディレクトリを静的ファイルとして提供
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# ルートエンドポイント
@app.get("/")
def read_root():
    return {
        "message": "Text Summarizer API",
        "docs": "/api/docs",
        "version": "0.1.0"
    }


# 開発サーバー起動（直接実行時のみ）
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
