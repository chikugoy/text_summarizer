import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import logging
import time
import sys

from app.api import api_router
from app.config import settings
from app.database import engine, Base

# 直接標準エラー出力にメッセージを出力（デバッグ用）
print("main.py が実行されました", file=sys.stderr)
sys.stderr.flush()

# ロガーの取得
logger = logging.getLogger(__name__)

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

# リクエストロギングミドルウェアの追加
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # リクエスト情報をログに記録
    logger.info(f"リクエスト開始: {request.method} {request.url.path}")
    
    # リクエストの処理
    response = await call_next(request)
    
    # 処理時間の計算
    process_time = time.time() - start_time
    
    # レスポンス情報をログに記録
    logger.info(f"リクエスト完了: {request.method} {request.url.path} - ステータス: {response.status_code} - 処理時間: {process_time:.4f}秒")
    
    return response

# APIルーターの登録
app.include_router(api_router, prefix="/api")

# アップロードディレクトリを静的ファイルとして提供
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# アプリケーション起動時のログ
logger.info(f"{settings.APP_NAME} アプリケーションが起動しました")

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
