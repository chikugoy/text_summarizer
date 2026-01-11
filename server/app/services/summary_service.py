"""テキスト要約サービスモジュール

LiteLLMを使用して複数のAIプロバイダーでテキスト要約を行う。
"""

import logging
import os
import time
from typing import List, Optional

import litellm
from litellm import completion

from app.config import settings

# LiteLLMの設定
litellm.drop_params = True

# ロガーの設定
logger = logging.getLogger(__name__)


# プロンプトテンプレート定数
class PromptTemplates:
    """プロンプトテンプレートを管理するクラス"""

    SYSTEM = "あなたは優秀なアシスタントです。"

    DEFAULT_INSTRUCTION = (
        "以下のテキストを要約してください。"
        "要点を簡潔にまとめ、重要な情報を保持してください。"
    )

    CHUNK = """
{instructions}

テキスト:
{text}

結果:
"""

    DIRECT = """
{instructions}

テキスト:
{text}

結果:
"""


class TextSplitter:
    """テキスト分割を担当するクラス"""

    @staticmethod
    def split_by_paragraphs(text: str, max_length: int) -> List[str]:
        """テキストを段落ごとに分割する

        Args:
            text: 分割するテキスト
            max_length: チャンクの最大長

        Returns:
            分割されたテキストのリスト
        """
        paragraphs = [p for p in text.split("\n\n") if p.strip()]
        chunks: List[str] = []
        current_chunk = ""

        for para in paragraphs:
            if len(current_chunk) + len(para) + 2 <= max_length:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks


class AIClient:
    """AI APIクライアントを管理するクラス"""

    def __init__(self, model: str, api_key: str):
        """初期化

        Args:
            model: 使用するAIモデル名
            api_key: APIキー
        """
        self.model = model
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
            Exception: API呼び出しに失敗した場合
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

            except Exception as e:
                error_str = str(e).lower()
                is_rate_limit = "rate_limit" in error_str or "429" in error_str

                if is_rate_limit and attempt < settings.AI_MAX_RETRIES - 1:
                    delay = settings.AI_RETRY_DELAY * (2**attempt)
                    logger.warning(
                        f"レート制限エラー。{delay}秒後にリトライします "
                        f"(試行 {attempt + 1}/{settings.AI_MAX_RETRIES})"
                    )
                    time.sleep(delay)
                else:
                    logger.error(f"API呼び出し失敗: {e}")
                    raise


class SummaryService:
    """テキスト要約サービス

    テキストを要約またはカスタム指示に従って処理する。
    """

    def __init__(self):
        """初期化"""
        self.model = settings.AI_MODEL
        self.api_key = settings.get_api_key_for_model(self.model)
        self.client: Optional[AIClient] = None

        if self.api_key:
            self.client = AIClient(self.model, self.api_key)
            logger.info(f"SummaryService初期化完了: モデル={self.model}")
        else:
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
        """
        if not self.client:
            return "処理エンジンが初期化されていません。APIキーを設定してください。"

        if not text:
            return ""

        # テキストのエンコーディングを統一
        try:
            text = text.encode("utf-8", errors="ignore").decode("utf-8")
        except Exception as e:
            logger.error(f"テキストエンコーディング処理エラー: {e}")
            return f"テキスト処理中にエラーが発生しました: {e}"

        instructions = custom_instructions or PromptTemplates.DEFAULT_INSTRUCTION
        logger.info(f"処理開始: テキスト長={len(text)}, 指示={instructions[:50]}...")

        try:
            if len(text) > max_length:
                return self._process_long_text(text, max_length, instructions)
            else:
                return self._process_short_text(text, instructions)
        except Exception as e:
            logger.error(f"処理エラー: {e}")
            return f"処理中にエラーが発生しました: {e}"

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
        """
        logger.info("長いテキストを分割して処理します")

        chunks = TextSplitter.split_by_paragraphs(text, max_length)
        results: List[str] = []

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

            except Exception as e:
                error_msg = f"チャンク {i + 1} の処理中にエラー: {e}"
                logger.error(error_msg)
                results.append(f"[エラー: {e}]")

        if not results:
            return "処理中にエラーが発生しました。"

        return "\n\n".join(results)


# シングルトンインスタンス
summary_service = SummaryService()
