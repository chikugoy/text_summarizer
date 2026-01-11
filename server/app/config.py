"""アプリケーション設定モジュール"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """アプリケーション設定

    環境変数から設定を読み込み、アプリケーション全体で使用する設定値を管理する。
    """

    # アプリケーション設定
    APP_NAME: str = "TextSummarizer"
    DEBUG: bool = False  # 本番環境ではFalseがデフォルト
    SECRET_KEY: str = "change-me-in-production"
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]

    # データベース設定
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/text_summarizer_db"

    # ファイルストレージ設定
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # OCR設定
    OCR_LANGUAGE: str = "japanese"
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None

    # AI設定 - 使用するモデル
    AI_MODEL: str = "gpt-4o"

    # AI APIキー - 各プロバイダー個別に設定可能
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    COHERE_API_KEY: Optional[str] = None

    # 後方互換性のための汎用キー（非推奨）
    AI_API_KEY: Optional[str] = None

    # AI処理設定
    AI_MAX_RETRIES: int = 3
    AI_RETRY_DELAY: int = 60  # 秒
    AI_TEMPERATURE: float = 0.3
    AI_CHUNK_DELAY: int = 60  # チャンク処理間の待機時間（秒）

    @field_validator("UPLOAD_DIR")
    @classmethod
    def create_upload_dir(cls, v: str) -> str:
        """アップロードディレクトリが存在しない場合は作成する"""
        os.makedirs(v, exist_ok=True)
        return v

    def get_api_key_for_model(self, model: str) -> Optional[str]:
        """モデル名に対応するAPIキーを取得する

        Args:
            model: AIモデル名（例: gpt-4o, claude-3-opus, gemini-pro）

        Returns:
            対応するAPIキー、見つからない場合はNone
        """
        # モデル名からプロバイダーを判定してAPIキーを返す
        if model.startswith("gpt-") or model.startswith("o1-"):
            return self.OPENAI_API_KEY or self.AI_API_KEY
        elif model.startswith("claude-"):
            return self.ANTHROPIC_API_KEY or self.AI_API_KEY
        elif model.startswith("gemini-"):
            return self.GEMINI_API_KEY or self.AI_API_KEY
        elif model.startswith("command-"):
            return self.COHERE_API_KEY or self.AI_API_KEY
        else:
            # デフォルトでOpenAIキーまたは汎用キーを使用
            return self.OPENAI_API_KEY or self.AI_API_KEY

    def get_provider_for_model(self, model: str) -> str:
        """モデル名からプロバイダー名を取得する

        Args:
            model: AIモデル名

        Returns:
            プロバイダー名（openai, anthropic, gemini, cohere）
        """
        # プレフィックス付きモデル名の場合
        if model.startswith("gemini/"):
            return "gemini"

        if model.startswith("gpt-") or model.startswith("o1-"):
            return "openai"
        elif model.startswith("claude-"):
            return "anthropic"
        elif model.startswith("gemini-"):
            return "gemini"
        elif model.startswith("command-"):
            return "cohere"
        return "openai"  # デフォルト

    def get_litellm_model_name(self, model: str) -> str:
        """LiteLLM用のモデル名を取得する

        LiteLLMでは、Google AI Studio（APIキー認証）を使用する場合、
        モデル名に 'gemini/' プレフィックスが必要。

        Args:
            model: AIモデル名

        Returns:
            LiteLLM用のモデル名
        """
        # 既にプレフィックスが付いている場合はそのまま返す
        if "/" in model:
            return model

        # Geminiモデルの場合、gemini/ プレフィックスを付ける
        if model.startswith("gemini-"):
            return f"gemini/{model}"

        return model

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore",
    }


# 設定インスタンスを作成
settings = Settings()
