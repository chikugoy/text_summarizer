"""カスタム例外クラス

アプリケーション固有の例外を定義し、適切なエラーハンドリングを実現する。
"""

from typing import Any, Optional


class AppException(Exception):
    """アプリケーション基底例外クラス"""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        detail: Optional[Any] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(message)


class ResourceNotFoundError(AppException):
    """リソースが見つからない場合の例外"""

    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type}が見つかりません: {resource_id}"
        super().__init__(message=message, status_code=404)


class ValidationError(AppException):
    """バリデーションエラー"""

    def __init__(self, message: str, detail: Optional[Any] = None):
        super().__init__(message=message, status_code=400, detail=detail)


class OCRProcessingError(AppException):
    """OCR処理エラー"""

    def __init__(self, message: str = "OCR処理中にエラーが発生しました"):
        super().__init__(message=message, status_code=500)


class SummaryGenerationError(AppException):
    """要約生成エラー"""

    def __init__(self, message: str = "要約の生成中にエラーが発生しました"):
        super().__init__(message=message, status_code=500)


class AIClientError(AppException):
    """AIクライアントエラーの基底クラス"""

    def __init__(self, message: str):
        super().__init__(message=message, status_code=502)


class RateLimitError(AIClientError):
    """レート制限エラー"""

    def __init__(self, retry_after: Optional[int] = None):
        message = "APIのレート制限に達しました"
        if retry_after:
            message += f" ({retry_after}秒後に再試行可能)"
        super().__init__(message=message)
        self.retry_after = retry_after


class APIConnectionError(AIClientError):
    """API接続エラー"""

    def __init__(self, provider: str):
        message = f"{provider} APIへの接続に失敗しました"
        super().__init__(message=message)


class ConfigurationError(AppException):
    """設定エラー"""

    def __init__(self, message: str):
        super().__init__(message=message, status_code=500)


class FileOperationError(AppException):
    """ファイル操作エラー"""

    def __init__(self, operation: str, path: str, detail: Optional[str] = None):
        message = f"ファイル{operation}に失敗しました: {path}"
        if detail:
            message += f" ({detail})"
        super().__init__(message=message, status_code=500)
