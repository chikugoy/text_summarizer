# 遅延インポートを避けるために、直接インポートしないサービスもあります
from app.services.summary_service import summary_service
from app.services.file_service import file_service

# OCRサービスは必要になった時点でインポートされます
# from app.services.ocr_service import ocr_service

# サービスをここにインポートすることで、他のモジュールから簡単にインポートできるようになります
# 例: from app.services import summary_service, file_service

# OCRサービスを取得する関数
def get_ocr_service():
    from app.services.ocr_service import ocr_service
    return ocr_service
