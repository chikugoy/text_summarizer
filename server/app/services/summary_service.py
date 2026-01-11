"""テキスト要約サービスモジュール

LiteLLMを使用して複数のAIプロバイダーでテキスト要約を行う。
"""

import logging
import os
import time
from typing import List, Optional

import litellm
from litellm import completion
from litellm.exceptions import RateLimitError as LiteLLMRateLimitError

from app.config import settings
from app.exceptions import (
    AIClientError,
    ConfigurationError,
    RateLimitError,
    SummaryGenerationError,
)
from app.services.prompts import PromptTemplates
from app.services.text_utils import TextSplitter

# LiteLLMの設定
litellm.drop_params = True

# ロガーの設定
logger = logging.getLogger(__name__)


class AIClient:
    """AI APIクライアントを管理するクラス"""

    def __init__(self, model: str, api_key: str):
        """初期化

        Args:
            model: 使用するAIモデル名
            api_key: APIキー
        """
        # LiteLLM用のモデル名に変換
        self.model = settings.get_litellm_model_name(model)
        self.api_key = api_key
        self._setup_environment()

    def _setup_environment(self) -> None:
        """LiteLLM用の環境変数を設定する"""
        provider = settings.get_provider_for_model(self.model)

        env_key_mapping = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "gemini": "GEMINI_API_KEY",
            "cohere": "COHERE_API_KEY",
        }

        env_key = env_key_mapping.get(provider, "OPENAI_API_KEY")
        os.environ[env_key] = self.api_key
        logger.info(f"AIクライアント初期化: モデル={self.model}, プロバイダー={provider}")

    def call(
        self,
        prompt: str,
        system_prompt: str = PromptTemplates.SYSTEM,
        temperature: Optional[float] = None,
    ) -> str:
        """AIモデルを呼び出す

        Args:
            prompt: ユーザープロンプト
            system_prompt: システムプロンプト
            temperature: 生成の温度パラメータ

        Returns:
            AIの応答テキスト

        Raises:
            RateLimitError: レート制限に達した場合
            AIClientError: API呼び出しに失敗した場合
        """
        temp = temperature if temperature is not None else settings.AI_TEMPERATURE

        for attempt in range(settings.AI_MAX_RETRIES):
            try:
                response = completion(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=temp,
                )
                return response.choices[0].message.content

            except LiteLLMRateLimitError as e:
                if attempt < settings.AI_MAX_RETRIES - 1:
                    delay = settings.AI_RETRY_DELAY * (2**attempt)
                    logger.warning(
                        f"レート制限エラー。{delay}秒後にリトライします "
                        f"(試行 {attempt + 1}/{settings.AI_MAX_RETRIES})"
                    )
                    time.sleep(delay)
                else:
                    logger.error(f"レート制限エラー: リトライ上限に達しました")
                    raise RateLimitError() from e
            except (ConnectionError, TimeoutError) as e:
                logger.error(f"接続エラー: {e}")
                raise AIClientError(f"AI APIへの接続に失敗しました: {e}") from e


class SummaryService:
    """テキスト要約サービス

    テキストを要約またはカスタム指示に従って処理する。
    """

    def __init__(self, client: Optional[AIClient] = None):
        """初期化

        Args:
            client: AIクライアント（省略時は設定から自動生成）
        """
        self.model = settings.AI_MODEL
        self.api_key = settings.get_api_key_for_model(self.model)

        if client:
            self.client = client
            logger.info(f"SummaryService初期化完了: 外部クライアント使用")
        elif self.api_key:
            self.client = AIClient(self.model, self.api_key)
            logger.info(f"SummaryService初期化完了: モデル={self.model}")
        else:
            self.client = None
            logger.warning(
                "APIキーが設定されていません。要約機能は利用できません。"
                "環境変数でOPENAI_API_KEY、ANTHROPIC_API_KEY等を設定してください。"
            )

    def summarize_text(
        self,
        text: str,
        max_length: int = 1000000,
        custom_instructions: Optional[str] = None,
    ) -> str:
        """テキストを処理する

        Args:
            text: 処理するテキスト
            max_length: チャンク分割の閾値
            custom_instructions: カスタム指示（省略時はデフォルトの要約指示）

        Returns:
            処理結果のテキスト

        Raises:
            ConfigurationError: クライアントが初期化されていない場合
            SummaryGenerationError: 要約生成に失敗した場合
        """
        if not self.client:
            raise ConfigurationError(
                "処理エンジンが初期化されていません。APIキーを設定してください。"
            )

        if not text:
            return ""

        # テキストのエンコーディングを統一
        try:
            text = text.encode("utf-8", errors="ignore").decode("utf-8")
        except UnicodeError as e:
            logger.error(f"テキストエンコーディング処理エラー: {e}")
            raise SummaryGenerationError(f"テキスト処理中にエラーが発生しました: {e}") from e

        instructions = custom_instructions or PromptTemplates.DEFAULT_INSTRUCTION
        logger.info(f"処理開始: テキスト長={len(text)}, 指示={instructions[:50]}...")

        try:
            if len(text) > max_length:
                return self._process_long_text(text, max_length, instructions)
            else:
                return self._process_short_text(text, instructions)
        except (RateLimitError, AIClientError) as e:
            logger.error(f"AI API処理エラー: {e}")
            raise SummaryGenerationError(str(e)) from e

    def _process_short_text(self, text: str, instructions: str) -> str:
        """短いテキストを直接処理する

        Args:
            text: 処理するテキスト
            instructions: 処理指示

        Returns:
            処理結果
        """
        logger.info("短いテキストを直接処理します")
        prompt = PromptTemplates.DIRECT.format(instructions=instructions, text=text)
        result = self.client.call(prompt)
        logger.info("処理完了")
        return result

    def _process_long_text(
        self, text: str, max_length: int, instructions: str
    ) -> str:
        """長いテキストを分割して処理する

        Args:
            text: 処理するテキスト
            max_length: チャンクの最大長
            instructions: 処理指示

        Returns:
            処理結果（各チャンクの結果を結合）

        Raises:
            SummaryGenerationError: 全てのチャンク処理に失敗した場合
        """
        logger.info("長いテキストを分割して処理します")

        chunks = TextSplitter.split_by_paragraphs(text, max_length)
        results: List[str] = []
        errors: List[str] = []

        for i, chunk in enumerate(chunks):
            try:
                logger.info(f"チャンク {i + 1}/{len(chunks)} を処理中...")
                prompt = PromptTemplates.CHUNK.format(
                    instructions=instructions, text=chunk
                )
                chunk_result = self.client.call(prompt)
                results.append(chunk_result)
                logger.info(f"チャンク {i + 1} の処理完了")

                # レート制限対策のため待機（最後のチャンク以外）
                if i < len(chunks) - 1:
                    time.sleep(settings.AI_CHUNK_DELAY)

            except RateLimitError:
                error_msg = f"チャンク {i + 1}: レート制限エラー"
                logger.error(error_msg)
                errors.append(error_msg)
            except AIClientError as e:
                error_msg = f"チャンク {i + 1}: {e.message}"
                logger.error(error_msg)
                errors.append(error_msg)

        if not results:
            raise SummaryGenerationError(
                f"全てのチャンク処理に失敗しました: {'; '.join(errors)}"
            )

        if errors:
            logger.warning(f"一部のチャンク処理に失敗: {errors}")

        return "\n\n".join(results)


# シングルトンインスタンス
summary_service = SummaryService()
