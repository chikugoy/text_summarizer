import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    """アプリケーション設定"""
    
    # アプリケーション設定
    APP_NAME: str = "TextSummarizer"
    DEBUG: bool = True
    SECRET_KEY: str
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    
    # データベース設定
    DATABASE_URL: str
    
    # ファイルストレージ設定
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # OCR設定
    OCR_LANGUAGE: str = "japanese"
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    
    # AI設定
    OPENAI_API_KEY: Optional[str] = None
    AI_MODEL: str = "gpt-3.5-turbo"
    
    @validator("UPLOAD_DIR")
    def create_upload_dir(cls, v):
        """アップロードディレクトリが存在しない場合は作成する"""
        os.makedirs(v, exist_ok=True)
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 設定インスタンスを作成
settings = Settings()
