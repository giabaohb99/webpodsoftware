import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
import logging
from fastapi import UploadFile
import uuid
import io
from typing import Union

from .config import settings

# Configure logging
logger = logging.getLogger(__name__)

class S3Storage:
    def __init__(self):
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION_NAME
            )
            self.bucket_name = settings.AWS_S3_BUCKET_NAME
            logger.info("S3 client initialized successfully.")
        except (NoCredentialsError, PartialCredentialsError) as e:
            logger.error(f"AWS credentials not found or incomplete: {e}")
            self.s3_client = None
        except Exception as e:
            logger.error(f"Error initializing S3 client: {e}")
            self.s3_client = None

    def upload_file(self, file: UploadFile, object_name: str = None) -> Union[str, None]:
        if not self.s3_client:
            logger.error("S3 client not available. Cannot upload file.")
            return None

        if object_name is None:
            # Generate a unique object name using UUID and original filename
            file_extension = file.filename.split('.')[-1]
            object_name = f"uploads/{uuid.uuid4()}.{file_extension}"

        try:
            self.s3_client.upload_fileobj(
                file.file,
                self.bucket_name,
                object_name,
                ExtraArgs={'ContentType': file.content_type}
            )
            file_url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION_NAME}.amazonaws.com/{object_name}"
            logger.info(f"File {file.filename} uploaded to {file_url}")
            return file_url
        except ClientError as e:
            logger.error(f"Failed to upload {file.filename} to S3: {e}")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred during file upload: {e}")
            return None

    def upload_file_from_bytes(self, file_data: bytes, filename: str, content_type: str = None) -> Union[str, None]:
        """Upload file from bytes data to S3"""
        if not self.s3_client:
            logger.error("S3 client not available. Cannot upload file.")
            return None

        try:
            # Create file-like object from bytes
            file_obj = io.BytesIO(file_data)
            
            # Set extra args
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            
            # Upload to S3
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                filename,
                ExtraArgs=extra_args
            )
            
            file_url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION_NAME}.amazonaws.com/{filename}"
            logger.info(f"File {filename} uploaded to {file_url}")
            return file_url
            
        except ClientError as e:
            logger.error(f"Failed to upload {filename} to S3: {e}")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred during file upload: {e}")
            return None

    def download_file_as_bytes(self, file_url: str) -> Union[bytes, None]:
        """Download file from S3 and return as bytes"""
        if not self.s3_client:
            logger.error("S3 client not available. Cannot download file.")
            return None

        try:
            # Extract object key from URL
            # Expected format: https://bucket.s3.region.amazonaws.com/path/to/file
            if f"{self.bucket_name}.s3.{settings.AWS_REGION_NAME}.amazonaws.com" in file_url:
                object_key = file_url.split(f"{self.bucket_name}.s3.{settings.AWS_REGION_NAME}.amazonaws.com/")[1]
            else:
                logger.error(f"Invalid S3 URL format: {file_url}")
                return None
            
            # Download file to bytes
            file_obj = io.BytesIO()
            self.s3_client.download_fileobj(self.bucket_name, object_key, file_obj)
            file_obj.seek(0)
            
            logger.info(f"File {object_key} downloaded successfully")
            return file_obj.getvalue()
            
        except ClientError as e:
            logger.error(f"Failed to download file from S3: {e}")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred during file download: {e}")
            return None

    def delete_file(self, file_url: str) -> bool:
        """Delete file from S3"""
        if not self.s3_client:
            logger.error("S3 client not available. Cannot delete file.")
            return False

        try:
            # Extract object key from URL
            if f"{self.bucket_name}.s3.{settings.AWS_REGION_NAME}.amazonaws.com" in file_url:
                object_key = file_url.split(f"{self.bucket_name}.s3.{settings.AWS_REGION_NAME}.amazonaws.com/")[1]
            else:
                logger.error(f"Invalid S3 URL format: {file_url}")
                return False
            
            # Delete file from S3
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=object_key)
            logger.info(f"File {object_key} deleted successfully")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to delete file from S3: {e}")
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred during file deletion: {e}")
            return False

# Create a single instance to be used across the application
s3_storage = S3Storage() 