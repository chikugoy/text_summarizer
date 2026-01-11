"""OCRオーケストレーターモジュール

OCRサービスとジョブマネージャーを統合し、複数画像の処理を管理する。
"""

import logging
from typing import Any, Dict, List, Optional

from app.exceptions import OCRProcessingError
from app.models import Image
from app.services.job_manager import JobManager, OCRResult, job_manager
from app.services.ocr_service import BaseOCRService, get_ocr_service

logger = logging.getLogger(__name__)


class OCROrchestrator:
    """OCR処理を統括するクラス

    OCRサービスとジョブマネージャーを組み合わせて、
    複数の画像を効率的に処理する。
    """

    def __init__(
        self,
        ocr_service: Optional[BaseOCRService] = None,
        job_mgr: Optional[JobManager] = None,
    ):
        """初期化

        Args:
            ocr_service: OCRサービス（省略時はデフォルトを使用）
            job_mgr: ジョブマネージャー（省略時はグローバルインスタンスを使用）
        """
        self._ocr_service = ocr_service or get_ocr_service()
        self._job_manager = job_mgr or job_manager

    def process_images(self, images: List[Image]) -> str:
        """複数の画像を処理し、ジョブIDを返す

        Args:
            images: 処理する画像リスト

        Returns:
            ジョブID
        """
        if not images:
            raise ValueError("処理する画像がありません")

        # ジョブを作成
        job_id = self._job_manager.create_job(total_images=len(images))
        logger.info(f"OCR処理開始: job_id={job_id}, images={len(images)}")

        success_count = 0
        error_count = 0

        for image in images:
            try:
                ocr_text = self._ocr_service.process_image(image.file_path)
                result = OCRResult(
                    image_id=str(image.id),
                    ocr_text=ocr_text,
                    success=True,
                )
                success_count += 1
            except OCRProcessingError as e:
                logger.error(f"OCR処理失敗: image_id={image.id}, error={e.message}")
                result = OCRResult(
                    image_id=str(image.id),
                    ocr_text="",
                    success=False,
                    error=e.message,
                )
                error_count += 1
            except (OSError, IOError) as e:
                logger.error(f"ファイル読み取りエラー: image_id={image.id}, error={e}")
                result = OCRResult(
                    image_id=str(image.id),
                    ocr_text="",
                    success=False,
                    error=f"ファイル読み取りエラー: {e}",
                )
                error_count += 1

            self._job_manager.add_result(job_id, result)

        # ジョブを完了
        all_success = error_count == 0
        self._job_manager.complete_job(job_id, success=all_success)

        logger.info(
            f"OCR処理完了: job_id={job_id}, success={success_count}, errors={error_count}"
        )

        return job_id

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """ジョブのステータスを取得する

        Args:
            job_id: ジョブID

        Returns:
            ジョブステータス情報
        """
        return self._job_manager.get_job_status(job_id)


# グローバルインスタンス
ocr_orchestrator = OCROrchestrator()
