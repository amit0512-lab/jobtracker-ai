import os
import uuid
import aiofiles
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings


class StorageService:

    # ─── Upload File ──────────────────────────────────────────

    @staticmethod
    async def upload_file(file: UploadFile, folder: str = "resumes") -> dict:
        """
        File upload karo — local ya S3
        Returns: { filename, file_path, file_size }
        """
        # File type check
        allowed_types = ["application/pdf", "application/msword",
                         "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sirf PDF aur Word documents allowed hain"
            )

        # Unique filename banao
        ext = file.filename.split(".")[-1]
        unique_name = f"{uuid.uuid4()}.{ext}"

        if settings.USE_LOCAL_STORAGE:
            return await StorageService._save_locally(file, folder, unique_name)
        else:
            return await StorageService._upload_to_s3(file, folder, unique_name)

    # ─── Local Save ───────────────────────────────────────────

    @staticmethod
    async def _save_locally(file: UploadFile, folder: str, filename: str) -> dict:
        save_dir = os.path.join(settings.LOCAL_STORAGE_PATH, folder)
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, filename)

        content = await file.read()
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

        file_size = f"{round(len(content) / 1024, 2)} KB"

        return {
            "filename": file.filename,
            "file_path": file_path,
            "file_size": file_size
        }

    # ─── S3 Upload (baad mein) ────────────────────────────────

    @staticmethod
    async def _upload_to_s3(file: UploadFile, folder: str, filename: str) -> dict:
        import boto3
        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        content = await file.read()
        s3_key = f"{folder}/{filename}"

        s3.put_object(
            Bucket=settings.AWS_BUCKET_NAME,
            Key=s3_key,
            Body=content,
            ContentType=file.content_type
        )

        file_path = f"https://{settings.AWS_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"
        file_size = f"{round(len(content) / 1024, 2)} KB"

        return {
            "filename": file.filename,
            "file_path": file_path,
            "file_size": file_size
        }

    # ─── Delete File ──────────────────────────────────────────

    @staticmethod
    async def delete_file(file_path: str):
        if settings.USE_LOCAL_STORAGE:
            if os.path.exists(file_path):
                os.remove(file_path)
        else:
            import boto3
            s3 = boto3.client("s3")
            key = file_path.split(".amazonaws.com/")[-1]
            s3.delete_object(Bucket=settings.AWS_BUCKET_NAME, Key=key)