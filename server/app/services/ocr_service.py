import os
import uuid
import sys
from typing import List, Dict, Any, Optional
from PIL import Image as PILImage

from app.config import settings
from app.models import Image

try:
    from google.cloud import vision
    from google.api_core.exceptions import GoogleAPICallError
    HAS_GOOGLE_VISION = True
except ImportError:
    HAS_GOOGLE_VISION = False

class BaseOCRService:
    """OCRサービスのベースクラス"""
    
    def __init__(self):
        self._jobs: Dict[str, Dict[str, Any]] = {}  # ジョブID -> ジョブ情報
    
    def process_image(self, image_path: str) -> str:
        """画像からテキストを抽出する（サブクラスで実装）"""
        raise NotImplementedError
    
    def process_images(self, images: List[Image]) -> str:
        """複数の画像を処理し、ジョブIDを返す"""
        job_id = str(uuid.uuid4())
        
        self._jobs[job_id] = {
            "images": images,
            "results": {},
            "status": "processing",
            "total": len(images),
            "completed": 0
        }
        
        for image in images:
            try:
                ocr_text = self.process_image(image.file_path)                
                print(f"ocr_text: {ocr_text}", file=sys.stderr)
                self._jobs[job_id]["results"][str(image.id)] = {
                    "image_id": image.id,
                    "ocr_text": ocr_text,
                    "success": True,
                    "error": None
                }
                self._jobs[job_id]["completed"] += 1
            except Exception as e:
                self._jobs[job_id]["results"][str(image.id)] = {
                    "image_id": image.id,
                    "ocr_text": "",
                    "success": False,
                    "error": str(e)
                }
                self._jobs[job_id]["completed"] += 1
        
        self._jobs[job_id]["status"] = "completed"
        return job_id
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """ジョブのステータスを取得する"""
        if job_id not in self._jobs:
            return None
        
        job = self._jobs[job_id]
        return {
            "job_id": job_id,
            "status": job["status"],
            "total": job["total"],
            "completed": job["completed"],
            "results": list(job["results"].values())
        }

class GoogleVisionOCRService(BaseOCRService):
    """Google Vision APIを使用したOCRサービス"""
    
    def __init__(self):
        super().__init__()
        self._client = None
    
    @property
    def client(self):
        """Google Visionクライアントを取得（遅延初期化）"""
        if self._client is None:
            self._client = vision.ImageAnnotatorClient()
        return self._client
    
    def process_image(self, image_path: str) -> str:
        """Google Vision APIで画像からテキストを抽出"""
        try:
            with open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            response = self.client.document_text_detection(image=image)
            
            if response.error.message:
                raise GoogleAPICallError(response.error.message)
            
            if response.full_text_annotation:
                return response.full_text_annotation.text
            return ""
        except GoogleAPICallError as e:
            print(f"Google Vision APIエラー: {str(e)}")
            return ""
        except Exception as e:
            print(f"OCR処理エラー: {str(e)}")
            return ""

class PaddleOCRService(BaseOCRService):
    """PaddleOCRを使用したOCRサービス"""
    
    def __init__(self):
        super().__init__()
        self._ocr = None
    
    @property
    def ocr(self):
        """PaddleOCRインスタンスを取得（遅延初期化）"""
        if self._ocr is None:
            from paddleocr import PaddleOCR
            self._ocr = PaddleOCR(use_angle_cls=True, lang=settings.OCR_LANGUAGE)
        return self._ocr
    
    def process_image(self, image_path: str) -> str:
        """PaddleOCRで画像からテキストを抽出"""
        try:
            img = PILImage.open(image_path)
            result = self.ocr.ocr(image_path, cls=True)
            
            extracted_text = ""
            if result:
                for line in result:
                    for word_info in line:
                        if len(word_info) >= 2:
                            text = word_info[1][0]
                            text = text.encode('utf-8', errors='ignore').decode('utf-8')
                            extracted_text += text + " "
                    extracted_text += "\n"
            
            return extracted_text.strip()
        except Exception as e:
            print(f"OCR処理エラー: {str(e)}")
            return ""

# 使用可能なOCRサービスを選択
if HAS_GOOGLE_VISION and os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
    ocr_service = GoogleVisionOCRService()
else:
    ocr_service = PaddleOCRService()
