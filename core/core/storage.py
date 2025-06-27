import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
import logging
from fastapi import UploadFile
import uuid
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

# Create a single instance to be used across the application
s3_storage = S3Storage() 