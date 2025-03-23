from fastapi import APIRouter

from app.api.endpoints import images, ocr, summaries

# メインAPIルーター
api_router = APIRouter()

# 各エンドポイントルーターを登録
api_router.include_router(images.router, prefix="/images", tags=["images"])
api_router.include_router(ocr.router, prefix="/ocr", tags=["ocr"])
api_router.include_router(summaries.router, prefix="/summaries", tags=["summaries"])
