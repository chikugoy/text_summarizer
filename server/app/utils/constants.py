"""アプリケーション定数モジュール

アプリケーション全体で使用する定数を定義する。
"""


class SummaryConstants:
    """要約関連の定数"""

    # 一時的な要約のタイトル（画像アップロード時に自動作成）
    TEMPORARY_TITLE = "一時的な要約"
    TEMPORARY_DESCRIPTION = "画像アップロード用の一時的な要約"


class ErrorMessages:
    """エラーメッセージの定数"""

    SUMMARY_NOT_FOUND = "ID {id} の要約が見つかりません"
    IMAGE_NOT_FOUND = "ID {id} の画像が見つかりません"
    OCR_PROCESSING_ERROR = "OCR処理中にエラーが発生しました"
    SUMMARY_GENERATION_ERROR = "要約生成中にエラーが発生しました"
    FILE_UPLOAD_ERROR = "ファイルアップロード中にエラーが発生しました"
