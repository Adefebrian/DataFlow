import os
import asyncio
import aiohttp
from fastapi import UploadFile
from src.config import get_settings

CHUNK_SIZE = 5 * 1024 * 1024


class StorageService:
    def __init__(self):
        self.settings = get_settings()
        self.use_r2 = bool(self.settings.R2_ACCOUNT_ID and self.settings.R2_BUCKET_NAME)

    async def stream_upload(
        self,
        file: UploadFile,
        storage_key: str,
    ) -> tuple[int, str]:
        if self.use_r2:
            bytes_written = await self._upload_to_r2(file, storage_key)
            return bytes_written, self.get_public_url(storage_key)
        else:
            return await self._upload_local(file, storage_key)

    async def _upload_local(self, file: UploadFile, storage_key: str) -> int:
        upload_dir = "/tmp/uploads"
        os.makedirs(upload_dir, exist_ok=True)

        safe_filename = storage_key.replace("/", "_")
        file_path = os.path.join(upload_dir, safe_filename)

        total_bytes = 0
        with open(file_path, "wb") as f:
            while True:
                chunk = await file.read(CHUNK_SIZE)
                if not chunk:
                    break
                f.write(chunk)
                total_bytes += len(chunk)

        return total_bytes, file_path

    async def _upload_to_r2(self, file: UploadFile, storage_key: str) -> int:
        import boto3
        from concurrent.futures import ThreadPoolExecutor

        s3_client = boto3.client(
            "s3",
            endpoint_url=f"https://{self.settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
            aws_access_key_id=self.settings.R2_ACCESS_KEY_ID,
            aws_secret_access_key=self.settings.R2_SECRET_ACCESS_KEY,
        )

        mpu = s3_client.create_multipart_upload(
            Bucket=self.settings.R2_BUCKET_NAME,
            Key=storage_key,
            ContentType=file.content_type or "application/octet-stream",
        )
        upload_id = mpu["UploadId"]
        parts = []
        part_number = 1
        total_bytes = 0

        try:
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as pool:
                while True:
                    chunk = await file.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    total_bytes += len(chunk)

                    part = await loop.run_in_executor(
                        pool,
                        lambda c=chunk, pn=part_number: s3_client.upload_part(
                            Bucket=self.settings.R2_BUCKET_NAME,
                            Key=storage_key,
                            PartNumber=pn,
                            UploadId=upload_id,
                            Body=c,
                        ),
                    )
                    parts.append({"PartNumber": part_number, "ETag": part["ETag"]})
                    part_number += 1

            s3_client.complete_multipart_upload(
                Bucket=self.settings.R2_BUCKET_NAME,
                Key=storage_key,
                UploadId=upload_id,
                MultipartUpload={"Parts": parts},
            )
            return total_bytes

        except Exception:
            s3_client.abort_multipart_upload(
                Bucket=self.settings.R2_BUCKET_NAME,
                Key=storage_key,
                UploadId=upload_id,
            )
            raise

    def get_public_url(self, storage_key: str) -> str:
        if self.use_r2:
            return f"https://{self.settings.R2_BUCKET_NAME}.{self.settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com/{storage_key}"
        return f"/tmp/uploads/{storage_key.replace('/', '_')}"

    async def delete(self, storage_key: str):
        if self.use_r2:
            import boto3

            s3_client = boto3.client(
                "s3",
                endpoint_url=f"https://{self.settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
                aws_access_key_id=self.settings.R2_ACCESS_KEY_ID,
                aws_secret_access_key=self.settings.R2_SECRET_ACCESS_KEY,
            )
            s3_client.delete_object(
                Bucket=self.settings.R2_BUCKET_NAME,
                Key=storage_key,
            )
        else:
            file_path = f"/tmp/uploads/{storage_key.replace('/', '_')}"
            if os.path.exists(file_path):
                os.remove(file_path)


storage_service = StorageService()


def get_r2_storage() -> StorageService:
    return storage_service
