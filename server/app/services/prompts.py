"""プロンプトテンプレート定義

AI処理用のプロンプトテンプレートを管理する。
"""


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
