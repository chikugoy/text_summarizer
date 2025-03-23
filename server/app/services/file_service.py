import os
import uuid
import shutil
from typing import List, Dict, Any, Optional
from fastapi import UploadFile

from app.config import settings


class FileService:
    """ファイル操作サービス"""
    
    def __init__(self):
        """アップロードディレクトリの初期化"""
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    async def save_upload_file(self, file: UploadFile, sub_dir: Optional[str] = None) -> Dict[str, Any]:
        """アップロードされたファイルを保存する"""
        # ファイル名の生成（UUID + 元のファイル名）
        file_id = str(uuid.uuid4())
        original_filename = file.filename or "unknown"
        filename = f"{file_id}_{original_filename}"
        
        # 保存先ディレクトリの設定
        save_dir = settings.UPLOAD_DIR
        if sub_dir:
            save_dir = os.path.join(save_dir, sub_dir)
            os.makedirs(save_dir, exist_ok=True)
        
        # ファイルパスの生成
        file_path = os.path.join(save_dir, filename)
        
        # ファイルの保存
        with open(file_path, "wb") as buffer:
            # ファイルの内容をコピー
            shutil.copyfileobj(file.file, buffer)
        
        # ファイル情報を返す
        return {
            "file_id": file_id,
            "file_name": original_filename,
            "file_path": file_path,
            "file_size": os.path.getsize(file_path),
            "mime_type": file.content_type or "application/octet-stream"
        }
    
    async def save_multiple_files(self, files: List[UploadFile], sub_dir: Optional[str] = None) -> List[Dict[str, Any]]:
        """複数のファイルを保存する"""
        results = []
        for i, file in enumerate(files):
            file_info = await self.save_upload_file(file, sub_dir)
            file_info["page_number"] = i + 1  # ページ番号を追加
            results.append(file_info)
        return results
    
    def delete_file(self, file_path: str) -> bool:
        """ファイルを削除する"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"ファイル削除エラー: {str(e)}")
            return False


# シングルトンインスタンス
file_service = FileService()
