from typing import List, Dict, Any, Optional
from langchain.chat_models import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
import os

from app.config import settings


class SummaryService:
    """テキスト要約サービス"""
    
    def __init__(self):
        """LLMの初期化"""
        # 環境変数を設定
        if settings.OPENAI_API_KEY:
            os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
            self.llm = ChatOpenAI(temperature=0, model_name=settings.AI_MODEL)
        else:
            self.llm = None
            print("警告: OPENAI_API_KEYが設定されていません。要約機能は利用できません。")
    
    def summarize_text(self, text: str, max_length: int = 2000) -> str:
        """テキストを要約する"""
        if not self.llm:
            return "要約エンジンが初期化されていません。環境変数OPENAI_API_KEYを設定してください。"
        
        if not text:
            return ""
        
        try:
            # テキストが長すぎる場合は分割
            if len(text) > max_length:
                chunks = self._split_text(text, max_length)
                docs = [Document(page_content=chunk) for chunk in chunks]
                chain = load_summarize_chain(self.llm, chain_type="map_reduce")
                summary = chain.run(docs)
            else:
                # 短いテキストの場合は直接要約
                prompt = f"""
                以下のテキストを要約してください。要点を簡潔にまとめ、重要な情報を保持してください。

                テキスト:
                {text}

                要約:
                """
                summary = self.llm(prompt)
            
            return summary.strip()
        except Exception as e:
            print(f"要約処理エラー: {str(e)}")
            return f"要約処理中にエラーが発生しました: {str(e)}"
    
    def _split_text(self, text: str, max_length: int = 2000) -> List[str]:
        """テキストを適切な長さに分割する"""
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
