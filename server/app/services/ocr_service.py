"""OCRサービスモジュール

Google Vision APIまたはPaddleOCRを使用して画像からテキストを抽出する。
"""

import logging
import os
import uuid
from typing import Any, Dict, List, Optional

from PIL import Image as PILImage

from app.config import settings
from app.exceptions import OCRProcessingError
from app.models import Image

logger = logging.getLogger(__name__)

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
                logger.debug(f"OCR結果: image_id={image.id}, text_length={len(ocr_text)}")
                self._jobs[job_id]["results"][str(image.id)] = {
                    "image_id": image.id,
                    "ocr_text": ocr_text,
                    "success": True,
                    "error": None,
                }
                self._jobs[job_id]["completed"] += 1
            except OCRProcessingError as e:
                logger.error(f"OCR処理失敗: image_id={image.id}, error={e.message}")
                self._jobs[job_id]["results"][str(image.id)] = {
                    "image_id": image.id,
                    "ocr_text": "",
                    "success": False,
                    "error": e.message,
                }
                self._jobs[job_id]["completed"] += 1
            except (OSError, IOError) as e:
                logger.error(f"ファイル読み取りエラー: image_id={image.id}, error={e}")
                self._jobs[job_id]["results"][str(image.id)] = {
                    "image_id": image.id,
                    "ocr_text": "",
                    "success": False,
                    "error": f"ファイル読み取りエラー: {e}",
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
            if settings.GOOGLE_APPLICATION_CREDENTIALS:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.GOOGLE_APPLICATION_CREDENTIALS
            self._client = vision.ImageAnnotatorClient()
        return self._client
    
    def process_image(self, image_path: str) -> str:
        """Google Vision APIで画像からテキストを抽出

        Args:
            image_path: 処理する画像のパス

        Returns:
            抽出されたテキスト

        Raises:
            OCRProcessingError: OCR処理に失敗した場合
        """
        try:
            with open(image_path, "rb") as image_file:
                content = image_file.read()

            image = vision.Image(content=content)
            response = self.client.document_text_detection(image=image)

            if response.error.message:
                raise GoogleAPICallError(response.error.message)

            if response.full_text_annotation:
                return response.full_text_annotation.text
            return ""
        except GoogleAPICallError as e:
            logger.error(f"Google Vision APIエラー: {e}")
            raise OCRProcessingError(f"Google Vision APIエラー: {e}") from e
        except FileNotFoundError as e:
            logger.error(f"画像ファイルが見つかりません: {image_path}")
            raise OCRProcessingError(f"画像ファイルが見つかりません: {image_path}") from e

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
        """PaddleOCRで画像からテキストを抽出

        Args:
            image_path: 処理する画像のパス

        Returns:
            抽出されたテキスト

        Raises:
            OCRProcessingError: OCR処理に失敗した場合
        """
        try:
            PILImage.open(image_path)  # 画像の検証
            result = self.ocr.ocr(image_path, cls=True)

            extracted_text = ""
            if result:
                for line in result:
                    for word_info in line:
                        if len(word_info) >= 2:
                            text = word_info[1][0]
                            text = text.encode("utf-8", errors="ignore").decode("utf-8")
                            extracted_text += text + " "
                    extracted_text += "\n"

            return extracted_text.strip()
        except FileNotFoundError as e:
            logger.error(f"画像ファイルが見つかりません: {image_path}")
            raise OCRProcessingError(f"画像ファイルが見つかりません: {image_path}") from e
        except (OSError, IOError) as e:
            logger.error(f"画像読み込みエラー: {image_path}, error={e}")
            raise OCRProcessingError(f"画像読み込みエラー: {e}") from e

def get_ocr_service() -> BaseOCRService:
    """使用可能なOCRサービスを取得する

    Google Vision APIの認証情報が設定されている場合はGoogle Visionを使用し、
    そうでない場合はPaddleOCRを使用する。

    Returns:
        OCRサービスインスタンス
    """
    if HAS_GOOGLE_VISION and settings.GOOGLE_APPLICATION_CREDENTIALS:
        logger.info(f"Google Vision OCRサービスを初期化")
        return GoogleVisionOCRService()
    else:
        logger.info("PaddleOCRサービスを初期化")
        return PaddleOCRService()


# デフォルトのOCRサービスインスタンス
ocr_service = get_ocr_service()
