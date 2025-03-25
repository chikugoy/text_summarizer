import logging
import sys
import os

# ログディレクトリの作成
log_dir = "./logs"
os.makedirs(log_dir, exist_ok=True)

# 直接標準エラー出力にメッセージを出力（デバッグ用）
print("app/__init__.py が実行されました", file=sys.stderr)
sys.stderr.flush()

# ロギングの基本設定
logging.basicConfig(
    level=logging.DEBUG,  # すべてのログを出力
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f"{log_dir}/app.log")  # ファイルにも出力
    ]
)

# 直接標準エラー出力にメッセージを出力（デバッグ用）
print(f"ロギング設定完了: ログファイル={log_dir}/app.log", file=sys.stderr)
sys.stderr.flush()

# デバッグモードの場合はより詳細なログを出力
try:
    from app.config import settings
    if settings.DEBUG:
        # appで始まるすべてのロガーのログレベルをDEBUGに設定
        for logger_name in logging.root.manager.loggerDict:
            if logger_name == 'app' or logger_name.startswith('app.'):
                logging.getLogger(logger_name).setLevel(logging.DEBUG)
        
        # ルートロガーも設定
        logging.getLogger().setLevel(logging.DEBUG)
        
        # 設定を確認するログ
        root_logger = logging.getLogger()
        root_logger.debug("ロギング設定完了: ルートロガーレベル=%s", root_logger.level)
        app_logger = logging.getLogger('app')
        app_logger.debug("ロギング設定完了: appロガーレベル=%s", app_logger.level)
except ImportError:
    pass  # 設定がまだロードされていない場合は無視