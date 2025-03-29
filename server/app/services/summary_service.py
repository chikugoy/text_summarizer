from typing import List, Dict, Any, Optional
import logging
import time
from openai import OpenAI, RateLimitError

from app.config import settings

# ロガーの設定
logger = logging.getLogger(__name__)

# プロンプトテンプレート
SYSTEM_PROMPT = "あなたは優秀な要約者です。"
CHUNK_PROMPT_TEMPLATE = """
以下のテキストの要点を簡潔にまとめてください:

{text}

要点:
"""

COMBINE_PROMPT_TEMPLATE = """
以下の複数の要約を統合して、全体の要約を作成してください:

{summaries}

統合された要約:
"""

DIRECT_SUMMARY_TEMPLATE = """
以下のテキストを要約してください。要点を簡潔にまとめ、重要な情報を保持してください。

テキスト:
{text}

要約:
"""

class SummaryService:
    """テキスト要約サービス"""
    
    def __init__(self):
        """初期化"""
        # APIキーの設定を確認
        if settings.OPENAI_API_KEY:
            logger.info(f"OpenAI APIキーが設定されています (長さ: {len(settings.OPENAI_API_KEY)})")
            self.api_key = settings.OPENAI_API_KEY
            self.model = settings.AI_MODEL
            self.client = OpenAI(api_key=self.api_key)
            logger.info(f"使用モデル: {self.model}")
        else:
            self.api_key = None
            self.model = None
            self.client = None
            logger.warning("OPENAI_API_KEYが設定されていません。要約機能は利用できません。")
    
    def summarize_text(self, text: str, max_length: int = 25000) -> str:
        """テキストを要約する"""
        if not self.api_key:
            return "要約エンジンが初期化されていません。環境変数OPENAI_API_KEYを設定してください。"
        
        if not text:
            return ""
            
        # テキストのエンコーディングを統一（UTF-8）
        try:
            text = text.encode('utf-8', errors='ignore').decode('utf-8')
        except Exception as e:
            logger.error(f"テキストエンコーディング処理エラー: {str(e)}")
            return f"テキスト処理中にエラーが発生しました: {str(e)}"
        
        try:
            logger.debug(f"テキスト長: {len(text)}")
            
            # テキストが長すぎる場合は分割して要約
            if len(text) > max_length:
                return self._summarize_long_text(text, max_length)
            else:
                # 短いテキストの場合は直接要約
                return self._summarize_short_text(text)
                
        except Exception as e:
            logger.error(f"要約処理エラー: {str(e)}")
            return f"要約処理中にエラーが発生しました: {str(e)}"
    
    def _summarize_long_text(self, text: str, max_length: int) -> str:
        """長いテキストを分割して要約する"""
        logger.info("長いテキストを分割して要約します")
        
        # 段落ごとにテキストを分割
        chunks = self._split_text_by_paragraphs(text, max_length)
        
        # 各チャンクを個別に要約
        summaries = []
        for i, chunk in enumerate(chunks):
            try:
                logger.info(f"チャンク {i+1}/{len(chunks)} を要約中...")
                chunk_summary = self._call_openai_api(
                    CHUNK_PROMPT_TEMPLATE.format(text=chunk)
                )
                summaries.append(chunk_summary)
                time.sleep(60)
                logger.info(f"チャンク {i+1} の要約が完了しました")
            except Exception as e:
                error_msg = f"チャンク {i+1} の要約中にエラーが発生しました: {str(e)}"
                logger.error(error_msg)
                summaries.append(f"要約エラー: {str(e)}")
        
        # 要約を結合
        if not summaries:
            return "要約処理中にエラーが発生しました。テキストが長すぎるか、形式が不適切です。"
            
        if len(summaries) == 1:
            return summaries[0]
        
        combined_summaries = "\n\n".join(summaries)
        return combined_summaries
        
        # # 結合した要約が短い場合はそのまま返す
        # if len(combined_summaries) < 4000:
        #     return combined_summaries
        
        # # 結合した要約をさらに要約
        # try:
        #     logger.info("最終要約を生成中...")
        #     final_summary = self._call_openai_api(
        #         COMBINE_PROMPT_TEMPLATE.format(summaries=combined_summaries)
        #     )
        #     logger.info("最終要約が完了しました")
        #     return final_summary
        # except Exception as e:
        #     error_msg = f"最終要約中にエラーが発生しました: {str(e)}"
        #     logger.error(error_msg)
        #     # エラーが発生した場合は結合した要約をそのまま返す
        #     return combined_summaries
    
    def _summarize_short_text(self, text: str) -> str:
        """短いテキストを直接要約する"""
        logger.info("短いテキストを直接要約します")
        try:
            prompt = DIRECT_SUMMARY_TEMPLATE.format(text=text)
            summary = self._call_openai_api(prompt)
            logger.info("要約が完了しました")
            return summary
        except Exception as e:
            error_msg = f"要約中にエラーが発生しました: {str(e)}"
            logger.error(error_msg)
            return f"要約処理中にエラーが発生しました: {str(e)}"
    
    def _call_openai_api(self, prompt: str) -> str:
        """OpenAI APIを呼び出す"""
        max_retries = 3
        retry_delay = 60  # 秒
        
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                )
                return response.choices[0].message.content
                
            except RateLimitError:
                if attempt < max_retries - 1:
                    logger.warning(f"Rate limit exceeded. Retrying in {retry_delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    raise
            except Exception as e:
                logger.error(f"OpenAI API call failed: {str(e)}")
                raise
    
    def _split_text_by_paragraphs(self, text: str, max_length: int) -> List[str]:
        """テキストを段落ごとに分割する"""
        paragraphs = [p for p in text.split('\n\n') if p.strip()]
        chunks = []
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
    
    def _split_text_by_words(self, text: str, max_length: int = 2000) -> List[str]:
        """テキストを単語単位で分割する"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 > max_length:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += len(word) + 1  # +1 for space
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks


# シングルトンインスタンス
summary_service = SummaryService()
