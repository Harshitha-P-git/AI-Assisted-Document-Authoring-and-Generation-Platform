import os
import boto3
from pathlib import Path
from typing import Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


def ensure_upload_dir():
    """Ensure upload directory exists"""
    upload_path = Path(settings.UPLOAD_DIR)
    upload_path.mkdir(parents=True, exist_ok=True)
    return upload_path


def save_file_locally(file_path: str, content: bytes) -> str:
    """Save file to local storage"""
    upload_dir = ensure_upload_dir()
    full_path = upload_dir / file_path
    
    # Create parent directories if needed
    full_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(full_path, "wb") as f:
        f.write(content)
    
    return str(full_path)


def get_file_locally(file_path: str) -> Optional[bytes]:
    """Get file from local storage"""
    upload_dir = ensure_upload_dir()
    full_path = upload_dir / file_path
    
    if not full_path.exists():
        return None
    
    with open(full_path, "rb") as f:
        return f.read()


def save_file_s3(file_path: str, content: bytes) -> str:
    """Save file to S3"""
    if not settings.USE_S3:
        raise Exception("S3 is not enabled")
    
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )
    
    s3_client.put_object(
        Bucket=settings.S3_BUCKET_NAME,
        Key=file_path,
        Body=content,
    )
    
    return f"s3://{settings.S3_BUCKET_NAME}/{file_path}"


def get_file_s3(file_path: str) -> Optional[bytes]:
    """Get file from S3"""
    if not settings.USE_S3:
        raise Exception("S3 is not enabled")
    
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )
    
    try:
        response = s3_client.get_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=file_path,
        )
        return response["Body"].read()
    except Exception as e:
        logger.error(f"Error getting file from S3: {e}")
        return None


def save_file(file_path: str, content: bytes) -> str:
    """Save file to configured storage (local or S3)"""
    if settings.USE_S3:
        return save_file_s3(file_path, content)
    else:
        return save_file_locally(file_path, content)


def get_file(file_path: str) -> Optional[bytes]:
    """Get file from configured storage (local or S3)"""
    if settings.USE_S3:
        return get_file_s3(file_path)
    else:
        return get_file_locally(file_path)

