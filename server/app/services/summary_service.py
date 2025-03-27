from typing import List, Dict, Any, Optional
import os

from app.config import settings


class SummaryService:
    """テキスト要約サービス"""
    
    def __init__(self):
        """初期化"""
        # APIキーの設定を確認
        if settings.OPENAI_API_KEY:
            print(f"DEBUG: OpenAI APIキーが設定されています (長さ: {len(settings.OPENAI_API_KEY)})")
            self.api_key = settings.OPENAI_API_KEY
            self.model = settings.AI_MODEL
            print(f"DEBUG: モデル: {self.model}")
        else:
            self.api_key = None
            self.model = None
            print("警告: OPENAI_API_KEYが設定されていません。要約機能は利用できません。")
    
    def summarize_text(self, text: str, max_length: int = 20000) -> str:
        """テキストを要約する"""
        if not self.api_key:
            return "要約エンジンが初期化されていません。環境変数OPENAI_API_KEYを設定してください。"
        
        if not text:
            return ""
            
        # テキストのエンコーディングを統一（UTF-8）
        try:
            text = text.encode('utf-8', errors='ignore').decode('utf-8')
        except Exception as e:
            print(f"テキストエンコーディング処理エラー: {str(e)}")
        
        try:
            print(f"len(text): {len(text)}")
            print(f"text: {text}")

            # テキストが長すぎる場合は分割
            if len(text) > max_length:
                print(f"step1-1")
    
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
                for i, chunk in enumerate(chunks):
                    try:
                        print(f"チャンク {i+1}/{len(chunks)} を要約中...")
                        chunk_prompt = f"""
                        以下のテキストの要点を簡潔にまとめてください:
                        
                        {chunk}
                        
                        要点:
                        """
                        
                        # 直接APIを呼び出す
                        from openai import OpenAI
                        client = OpenAI(api_key=self.api_key)
                        response = client.chat.completions.create(
                            model=self.model,
                            messages=[
                                {"role": "system", "content": "あなたは優秀な要約者です。"},
                                {"role": "user", "content": chunk_prompt}
                            ],
                            temperature=0.3,
                        )
                        chunk_summary = response.choices[0].message.content
                        summaries.append(chunk_summary)
                        print(f"チャンク {i+1} の要約が完了しました")
                    except Exception as e:
                        error_msg = f"チャンク {i+1} の要約中にエラーが発生しました: {str(e)}"
                        print(error_msg)
                        summaries.append(f"要約エラー: {str(e)}")
                
                # 要約を結合
                if summaries:
                    if len(summaries) == 1:
                        return summaries[0]
                    
                    combined_summaries = "\n\n".join(summaries)
                    
                    # 結合した要約が短い場合はそのまま返す
                    if len(combined_summaries) < 4000:
                        return combined_summaries
                    
                    # 結合した要約をさらに要約
                    try:
                        print("最終要約を生成中...")
                        final_prompt = f"""
                        以下の複数の要約を統合して、全体の要約を作成してください:
                        
                        {combined_summaries}
                        
                        統合された要約:
                        """
                        
                        # 直接APIを呼び出す
                        from openai import OpenAI
                        client = OpenAI(api_key=self.api_key)
                        response = client.chat.completions.create(
                            model=self.model,
                            messages=[
                                {"role": "system", "content": "あなたは優秀な要約者です。"},
                                {"role": "user", "content": final_prompt}
                            ],
                            temperature=0.3,
                        )
                        final_summary = response.choices[0].message.content
                        print("最終要約が完了しました")
                        return final_summary
                    except Exception as e:
                        error_msg = f"最終要約中にエラーが発生しました: {str(e)}"
                        print(error_msg)
                        # エラーが発生した場合は結合した要約をそのまま返す
                        return combined_summaries
                else:
                    return "要約処理中にエラーが発生しました。テキストが長すぎるか、形式が不適切です。"
            else:
                print(f"step2-1")

                # 短いテキストの場合は直接要約
                try:
                    print("短いテキストを直接要約中...")
                    prompt = f"""
                    以下のテキストを要約してください。要点を簡潔にまとめ、重要な情報を保持してください。

                    テキスト:
                    {text}

                    要約:
                    """
                    
                    # 直接APIを呼び出す
                    from openai import OpenAI
                    client = OpenAI(api_key=self.api_key)
                    response = client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": "あなたは優秀な要約者です。"},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.3,
                    )
                    summary = response.choices[0].message.content
                    print("要約が完了しました")
                    return summary
                except Exception as e:
                    error_msg = f"要約中にエラーが発生しました: {str(e)}"
                    print(error_msg)
                    return f"要約処理中にエラーが発生しました: {str(e)}"
            
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

    # 不要なメソッドを削除
    


# シングルトンインスタンス
summary_service = SummaryService()
