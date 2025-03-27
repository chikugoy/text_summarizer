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
            print(f"DEBUG: OpenAI APIキーが設定されています (長さ: {len(settings.OPENAI_API_KEY)})")
            os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
            os.environ["AI_MODEL"] = settings.AI_MODEL
            try:
                self.llm = ChatOpenAI(temperature=0, model_name=settings.AI_MODEL)
                print("DEBUG: LLMが正常に初期化されました")
            except Exception as e:
                print(f"DEBUG: LLM初期化エラー: {str(e)}")
                self.llm = None
        else:
            self.llm = None
            print("警告: OPENAI_API_KEYが設定されていません。要約機能は利用できません。")
    
    def summarize_text(self, text: str, max_length: int = 20000) -> str:
        """テキストを要約する"""
        if not self.llm:
            return "要約エンジンが初期化されていません。環境変数OPENAI_API_KEYを設定してください。"
        
        if not text:
            return ""
            
        # テキストのエンコーディングを統一（UTF-8）
        try:
            text = text.encode('utf-8', errors='ignore').decode('utf-8')
        except Exception as e:
            print(f"テキストエンコーディング処理エラー: {str(e)}")
        
        try:
            # テキストが長すぎる場合は分割
            if len(text) > max_length:
                # 段落ごとにテキストを分割
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

                # 各チャンクを個別に要約
                summaries = []
                for chunk in chunks:
                    try:
                        chunk_prompt = f"""
                        以下のテキストの要点を簡潔にまとめてください:
                        
                        {chunk}
                        
                        要点:
                        """
                        chunk_response = self.llm(chunk_prompt)
                        chunk_summary = str(chunk_response)
                        summaries.append(chunk_summary)
                    except Exception as e:
                        print(f"チャンク要約エラー: {str(e)}")
                        summaries.append(f"要約エラー: {str(e)}")
                
                # 要約を結合
                if summaries:
                    combined_summaries = "\n\n".join(summaries)
                    
                    # 結合した要約をさらに要約
                    final_prompt = f"""
                    以下の複数の要約を統合して、全体の要約を作成してください:
                    
                    {combined_summaries}
                    
                    統合された要約:
                    """
                    
                    try:
                        final_response = self.llm(final_prompt)
                        summary = str(final_response)
                    except Exception as e:
                        print(f"最終要約エラー: {str(e)}")
                        summary = combined_summaries
                else:
                    summary = "要約処理中にエラーが発生しました。テキストが長すぎるか、形式が不適切です。"
            else:
                # 短いテキストの場合は直接要約
                prompt = f"""
                以下のテキストを要約してください。要点を簡潔にまとめ、重要な情報を保持してください。

                テキスト:
                {text}

                要約:
                """
                response = self.llm(prompt)
                summary = str(response)  # 常に文字列に変換
            
            return summary.strip() if isinstance(summary, str) else str(summary)
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

    def _create_map_prompt(self):
        from langchain.prompts import PromptTemplate
        return PromptTemplate(
            template="""以下のテキストの要点を簡潔にまとめてください:
            
            {text}
            
            要点:
            """,
            input_variables=["text"]
        )

    def _create_combine_prompt(self):
        from langchain.prompts import PromptTemplate
        return PromptTemplate(
            template="""以下の複数の要約を統合して、全体の要約を作成してください:
            
            {text}
            
            統合された要約:
            """,
            input_variables=["text"]
        )
    


# シングルトンインスタンス
summary_service = SummaryService()
