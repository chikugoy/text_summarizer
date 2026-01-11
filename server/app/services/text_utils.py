"""テキスト処理ユーティリティ

テキストの分割や変換を行うユーティリティクラス。
"""

from typing import List


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

    @staticmethod
    def split_by_sentences(text: str, max_length: int) -> List[str]:
        """テキストを文ごとに分割する

        Args:
            text: 分割するテキスト
            max_length: チャンクの最大長

        Returns:
            分割されたテキストのリスト
        """
        # 日本語の句読点で分割
        delimiters = ["。", "！", "？", ".", "!", "?"]
        sentences: List[str] = []
        current = ""

        for char in text:
            current += char
            if char in delimiters:
                sentences.append(current.strip())
                current = ""

        if current.strip():
            sentences.append(current.strip())

        # チャンクに結合
        chunks: List[str] = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 <= max_length:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks
