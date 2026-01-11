"""アプリケーション定数モジュール

アプリケーション全体で使用する定数を定義する。
"""


class SummaryConstants:
    """要約関連の定数"""

    # 一時的な要約のタイトル（画像アップロード時に自動作成）
    TEMPORARY_TITLE = "一時的な要約"
    TEMPORARY_DESCRIPTION = "画像アップロード用の一時的な要約"


class AIConstants:
    """AI処理関連の定数"""

    # テキスト処理の閾値
    DEFAULT_MAX_LENGTH = 1000000  # チャンク分割の閾値
    DEFAULT_CHUNK_SIZE = 25000  # デフォルトのチャンクサイズ

    # リトライ設定
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_RETRY_DELAY = 60  # 秒


class PaginationConstants:
    """ページネーション関連の定数"""

    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100


class JobConstants:
    """ジョブ管理関連の定数"""

    # ジョブのクリーンアップ設定
    JOB_CLEANUP_HOURS = 24  # 古いジョブを削除するまでの時間


class ErrorMessages:
    """エラーメッセージの定数"""

    # リソース関連
    SUMMARY_NOT_FOUND = "ID {id} の要約が見つかりません"
    IMAGE_NOT_FOUND = "ID {id} の画像が見つかりません"
    JOB_NOT_FOUND = "ID {id} のジョブが見つかりません"

    # 処理エラー
    OCR_PROCESSING_ERROR = "OCR処理中にエラーが発生しました"
    SUMMARY_GENERATION_ERROR = "要約生成中にエラーが発生しました"
    FILE_UPLOAD_ERROR = "ファイルアップロード中にエラーが発生しました"

    # バリデーションエラー
    INVALID_UUID = "{field}が正しいUUID形式ではありません: {value}"
    INVALID_FILE_TYPE = "無効なファイル形式です: {type}"
    FILE_TOO_LARGE = "ファイルサイズが大きすぎます"

    # 設定エラー
    API_KEY_NOT_SET = "APIキーが設定されていません"
    SERVICE_NOT_INITIALIZED = "サービスが初期化されていません"
