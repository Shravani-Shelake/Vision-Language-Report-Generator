import os
import uuid
import boto3
from pathlib import Path
from fastapi import UploadFile
from config import settings
from typing import Tuple

class StorageService:
    def __init__(self):
        self.use_local = settings.USE_LOCAL_STORAGE
        if not self.use_local:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            self.bucket_name = settings.S3_BUCKET_NAME
        else:
            self.local_path = Path(settings.LOCAL_STORAGE_PATH)
            self.local_path.mkdir(parents=True, exist_ok=True)
    
    async def upload_file(self, file: UploadFile, file_type: str) -> Tuple[str, str]:
        """
        Upload file to S3 or local storage
        Returns: (file_id, storage_path)
        """
        file_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix
        storage_filename = f"{file_id}{file_extension}"
        
        # Read file content
        content = await file.read()
        await file.seek(0)  # Reset file pointer
        
        if self.use_local:
            # Local storage
            type_folder = self.local_path / file_type
            type_folder.mkdir(exist_ok=True)
            file_path = type_folder / storage_filename
            
            with open(file_path, "wb") as f:
                f.write(content)
            
            storage_path = str(file_path)
        else:
            # S3 storage
            s3_key = f"{file_type}/{storage_filename}"
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=content
            )
            storage_path = f"s3://{self.bucket_name}/{s3_key}"
        
        return file_id, storage_path
    
    def get_file_path(self, storage_path: str) -> str:
        """Get local file path from storage path"""
        if self.use_local:
            return storage_path
        else:
            # Download from S3 to temp location
            s3_key = storage_path.replace(f"s3://{self.bucket_name}/", "")
            temp_path = f"/tmp/{Path(s3_key).name}"
            self.s3_client.download_file(self.bucket_name, s3_key, temp_path)
            return temp_path