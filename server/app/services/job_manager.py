"""OCRジョブ管理モジュール

OCR処理のジョブを管理する。
"""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    """ジョブのステータス"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class OCRResult:
    """OCR処理結果"""

    image_id: str
    ocr_text: str
    success: bool
    error: Optional[str] = None


@dataclass
class Job:
    """ジョブ情報"""

    job_id: str
    status: JobStatus
    total: int
    completed: int = 0
    results: Dict[str, OCRResult] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "job_id": self.job_id,
            "status": self.status.value,
            "total": self.total,
            "completed": self.completed,
            "results": [
                {
                    "image_id": r.image_id,
                    "ocr_text": r.ocr_text,
                    "success": r.success,
                    "error": r.error,
                }
                for r in self.results.values()
            ],
        }


class JobManager:
    """OCRジョブを管理するクラス"""

    def __init__(self):
        self._jobs: Dict[str, Job] = {}

    def create_job(self, total_images: int) -> str:
        """新しいジョブを作成する

        Args:
            total_images: 処理する画像の総数

        Returns:
            ジョブID
        """
        job_id = str(uuid.uuid4())
        self._jobs[job_id] = Job(
            job_id=job_id,
            status=JobStatus.PROCESSING,
            total=total_images,
        )
        logger.info(f"ジョブ作成: job_id={job_id}, total={total_images}")
        return job_id

    def add_result(self, job_id: str, result: OCRResult) -> None:
        """ジョブに結果を追加する

        Args:
            job_id: ジョブID
            result: OCR処理結果
        """
        if job_id not in self._jobs:
            logger.warning(f"不明なジョブID: {job_id}")
            return

        job = self._jobs[job_id]
        job.results[result.image_id] = result
        job.completed += 1

        logger.debug(
            f"結果追加: job_id={job_id}, image_id={result.image_id}, "
            f"completed={job.completed}/{job.total}"
        )

    def complete_job(self, job_id: str, success: bool = True) -> None:
        """ジョブを完了状態にする

        Args:
            job_id: ジョブID
            success: 成功した場合True
        """
        if job_id not in self._jobs:
            logger.warning(f"不明なジョブID: {job_id}")
            return

        self._jobs[job_id].status = (
            JobStatus.COMPLETED if success else JobStatus.FAILED
        )
        logger.info(f"ジョブ完了: job_id={job_id}, status={self._jobs[job_id].status}")

    def get_job(self, job_id: str) -> Optional[Job]:
        """ジョブを取得する

        Args:
            job_id: ジョブID

        Returns:
            ジョブ情報、見つからない場合はNone
        """
        return self._jobs.get(job_id)

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """ジョブのステータスを辞書形式で取得する

        Args:
            job_id: ジョブID

        Returns:
            ジョブステータス情報
        """
        job = self.get_job(job_id)
        if job is None:
            return None
        return job.to_dict()

    def cleanup_old_jobs(self, max_age_hours: int = 24) -> int:
        """古いジョブを削除する

        Args:
            max_age_hours: 削除対象の経過時間（時間）

        Returns:
            削除されたジョブ数
        """
        from datetime import timedelta

        now = datetime.now()
        cutoff = now - timedelta(hours=max_age_hours)

        old_jobs = [
            job_id
            for job_id, job in self._jobs.items()
            if job.created_at < cutoff
        ]

        for job_id in old_jobs:
            del self._jobs[job_id]

        if old_jobs:
            logger.info(f"古いジョブを削除: {len(old_jobs)}件")

        return len(old_jobs)


# グローバルインスタンス
job_manager = JobManager()
