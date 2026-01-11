"""サービスインターフェース定義

依存性注入のためのプロトコルクラスを定義する。
"""

from typing import Any, Dict, List, Optional, Protocol

from app.models import Image


class IAIClient(Protocol):
    """AIクライアントのインターフェース"""

    def call(
        self,
        prompt: str,
        system_prompt: str = ...,
        temperature: Optional[float] = None,
    ) -> str:
        """AIモデルを呼び出す

        Args:
            prompt: ユーザープロンプト
            system_prompt: システムプロンプト
            temperature: 生成の温度パラメータ

        Returns:
            AIの応答テキスト
        """
        ...


class ISummaryService(Protocol):
    """要約サービスのインターフェース"""

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
            custom_instructions: カスタム指示

        Returns:
            処理結果のテキスト
        """
        ...


class IOCRService(Protocol):
    """OCRサービスのインターフェース"""

    def process_image(self, image_path: str) -> str:
        """画像からテキストを抽出する

        Args:
            image_path: 処理する画像のパス

        Returns:
            抽出されたテキスト
        """
        ...

    def process_images(self, images: List[Image]) -> str:
        """複数の画像を処理し、ジョブIDを返す

        Args:
            images: 処理する画像リスト

        Returns:
            ジョブID
        """
        ...

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """ジョブのステータスを取得する

        Args:
            job_id: ジョブID

        Returns:
            ジョブステータス情報
        """
        ...


class IFileService(Protocol):
    """ファイルサービスのインターフェース"""

    def save_uploaded_file(self, file: Any, filename: str) -> str:
        """アップロードされたファイルを保存する

        Args:
            file: アップロードされたファイル
            filename: ファイル名

        Returns:
            保存されたファイルのパス
        """
        ...

    def delete_file(self, file_path: str) -> bool:
        """ファイルを削除する

        Args:
            file_path: 削除するファイルのパス

        Returns:
            削除成功の場合True
        """
        ...
