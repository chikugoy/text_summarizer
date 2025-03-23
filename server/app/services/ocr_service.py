import os
import uuid
from typing import List, Dict, Any, Optional
from paddleocr import PaddleOCR
from PIL import Image as PILImage

from app.config import settings
from app.models import Image


class OCRService:
    """OCR処理サービス"""
    
    def __init__(self):
        """OCRエンジンの初期化"""
        self.ocr = PaddleOCR(use_angle_cls=True, lang=settings.OCR_LANGUAGE)
        self._jobs: Dict[str, Dict[str, Any]] = {}  # ジョブID -> ジョブ情報
    
    def process_image(self, image_path: str) -> str:
        """画像からテキストを抽出する"""
        try:
            # 画像を読み込む
            img = PILImage.open(image_path)
            
            # OCR処理を実行
            result = self.ocr.ocr(image_path, cls=True)
            
            # 結果を整形
            extracted_text = ""
            if result:
                for line in result:
                    for word_info in line:
                        if len(word_info) >= 2:  # 座標と(テキスト, 信頼度)のタプル
                            extracted_text += word_info[1][0] + " "
                    extracted_text += "\n"
            
            return extracted_text.strip()
        except Exception as e:
            # エラーログを出力
            print(f"OCR処理エラー: {str(e)}")
            return ""
    
    def process_images(self, images: List[Image]) -> str:
        """複数の画像を処理し、ジョブIDを返す"""
        job_id = str(uuid.uuid4())
        
        # ジョブ情報を保存
        self._jobs[job_id] = {
            "images": images,
            "results": {},
            "status": "processing",
            "total": len(images),
            "completed": 0
        }
        
        # 非同期処理を模倣（実際の実装では非同期タスクを使用）
        for image in images:
            try:
                ocr_text = self.process_image(image.file_path)
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
        
        # すべての処理が完了したらステータスを更新
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


# シングルトンインスタンス
ocr_service = OCRService()
