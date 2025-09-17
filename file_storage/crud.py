from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import Optional
from fastapi import UploadFile, HTTPException, status
import io
import os
from PIL import Image
import boto3
from botocore.exceptions import ClientError

from . import models, schemas

def create_file(db: Session, file: schemas.FileCreate) -> models.File:
    db_file = models.File(**file.dict())
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

def get_file(db: Session, file_id: int) -> Optional[models.File]:
    return db.query(models.File).filter(models.File.id == file_id).first()

def get_files(
    db: Session, 
    keyword: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    file_extension: Optional[str] = None,
    file_ids: Optional[list[int]] = None,
    content_type_prefix: Optional[str] = None,
    skip: int = 0, 
    limit: int = 100
):
    query = db.query(models.File)

    if file_ids:
        query = query.filter(models.File.id.in_(file_ids))

    if content_type_prefix:
        query = query.filter(models.File.content_type.ilike(f"{content_type_prefix}%"))

    if keyword:
        query = query.filter(models.File.filename.ilike(f"%{keyword}%"))
    
    if start_date:
        query = query.filter(models.File.created_at >= start_date)
    
    if end_date:
        query = query.filter(models.File.created_at <= end_date)
        
    if file_extension:
        # Ensure the extension doesn't have a leading dot
        clean_extension = file_extension.lstrip('.')
        query = query.filter(models.File.file_extension.ilike(f"%{clean_extension}%"))

    total = query.count()
    files = query.order_by(models.File.created_at.desc()).offset(skip).limit(limit).all()
    
    return {"total": total, "files": files} 

def upload_file(
    db: Session,
    file: UploadFile,
    s3_storage,
    validate_public: bool = False
) -> models.File:
    # Validate public upload
    if validate_public:
        allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp", "application/pdf"]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Chỉ cho phép upload ảnh hoặc PDF")
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        if file_size > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Dung lượng file tối đa 5MB")
    # Check s3 client
    if not s3_storage.s3_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="client is not available."
        )
    # Get file size before uploading
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    file_url = s3_storage.upload_file(file=file)
    if file_url is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload file to"
        )
    filename_parts = file.filename.split('.')
    file_extension = filename_parts[-1] if len(filename_parts) > 1 else None
    file_data = schemas.FileCreate(
        filename=file.filename,
        file_url=file_url,
        content_type=file.content_type,
        file_extension=file_extension,
        size=file_size
    )
    db_file = create_file(db=db, file=file_data)
    return db_file

# Thumbnail CRUD functions
def get_thumbnail(
    db: Session, 
    file_id: int, 
    width: int, 
    height: int, 
    format: str = "webp",
    quality: int = 80
) -> Optional[models.Thumbnail]:
    """Get existing thumbnail or return None"""
    return db.query(models.Thumbnail).filter(
        models.Thumbnail.original_file_id == file_id,
        models.Thumbnail.width == width,
        models.Thumbnail.height == height,
        models.Thumbnail.format == format,
        models.Thumbnail.quality == quality
    ).first()

def create_thumbnail(db: Session, thumbnail_data: schemas.ThumbnailCreate) -> models.Thumbnail:
    """Create new thumbnail record in database"""
    db_thumbnail = models.Thumbnail(**thumbnail_data.dict())
    db.add(db_thumbnail)
    db.commit()
    db.refresh(db_thumbnail)
    return db_thumbnail

def update_thumbnail_access(db: Session, thumbnail: models.Thumbnail):
    """Update last accessed time and access count"""
    thumbnail.last_accessed = datetime.utcnow()
    thumbnail.access_count += 1
    db.commit()

def resize_image(image_data: bytes, width: int, height: int, format: str = "webp", quality: int = 80) -> bytes:
    """Resize image using Pillow"""
    try:
        # Open image from bytes
        image = Image.open(io.BytesIO(image_data))
        
        # Convert RGBA to RGB if saving as JPEG
        if format.lower() in ['jpg', 'jpeg'] and image.mode in ('RGBA', 'LA', 'P'):
            # Create white background
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        
        # Resize image maintaining aspect ratio
        image.thumbnail((width, height), Image.Resampling.LANCZOS)
        
        # Save to bytes
        output = io.BytesIO()
        save_format = 'JPEG' if format.lower() in ['jpg', 'jpeg'] else format.upper()
        
        if save_format == 'JPEG':
            image.save(output, format=save_format, quality=quality, optimize=True)
        elif save_format == 'WEBP':
            image.save(output, format=save_format, quality=quality, optimize=True)
        else:
            image.save(output, format=save_format, optimize=True)
        
        return output.getvalue()
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resize image: {str(e)}"
        )

def upload_thumbnail_to_s3(s3_storage, thumbnail_data: bytes, file_id: int, width: int, height: int, format: str = "webp") -> str:
    """Upload thumbnail to S3 and return URL"""
    try:
        # Generate thumbnail filename
        thumbnail_filename = f"thumbnails/{file_id}_{width}x{height}.{format}"
        
        # Create file-like object from bytes
        thumbnail_file = io.BytesIO(thumbnail_data)
        thumbnail_file.name = thumbnail_filename
        
        # Set content type
        content_type_map = {
            'webp': 'image/webp',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png'
        }
        content_type = content_type_map.get(format.lower(), 'image/webp')
        
        # Upload to S3
        file_url = s3_storage.upload_file_from_bytes(
            file_data=thumbnail_data,
            filename=thumbnail_filename,
            content_type=content_type
        )
        
        if not file_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload thumbnail to S3"
            )
        
        return file_url
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload thumbnail: {str(e)}"
        )

def get_or_create_thumbnail(
    db: Session,
    s3_storage,
    file_id: int,
    width: int,
    height: int,
    format: str = "webp",
    quality: int = 80
) -> models.Thumbnail:
    """Main function: get existing thumbnail or create new one"""
    
    # Step 1: Check if thumbnail already exists
    existing_thumbnail = get_thumbnail(db, file_id, width, height, format, quality)
    if existing_thumbnail:
        # Update access stats
        update_thumbnail_access(db, existing_thumbnail)
        return existing_thumbnail
    
    # Step 2: Get original file
    original_file = get_file(db, file_id)
    if not original_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Original file not found"
        )
    
    # Step 3: Check if original file is an image
    if not original_file.content_type or not original_file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is not an image"
        )
    
    # Step 4: Download original image from S3
    try:
        original_image_data = s3_storage.download_file_as_bytes(original_file.file_url)
        if not original_image_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to download original image"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download original image: {str(e)}"
        )
    
    # Step 5: Resize image
    thumbnail_data = resize_image(original_image_data, width, height, format, quality)
    
    # Step 6: Upload thumbnail to S3
    thumbnail_url = upload_thumbnail_to_s3(s3_storage, thumbnail_data, file_id, width, height, format)
    
    # Step 7: Save thumbnail record to database
    thumbnail_create = schemas.ThumbnailCreate(
        original_file_id=file_id,
        width=width,
        height=height,
        quality=quality,
        format=format,
        file_url=thumbnail_url,
        file_size=len(thumbnail_data)
    )
    
    db_thumbnail = create_thumbnail(db, thumbnail_create)
    
    # Update access stats for new thumbnail
    update_thumbnail_access(db, db_thumbnail)
    
    return db_thumbnail

def generate_thumbnail_urls_for_file(file_id: int, base_url: str = "http://localhost:8000") -> list:
    """Generate thumbnail URLs for common sizes"""
    common_sizes = [
        (150, 150),   # Small thumbnail
        (300, 300),   # Medium thumbnail  
        (600, 600),   # Large thumbnail
        (800, 600),   # Landscape
    ]
    
    thumbnail_urls = []
    for width, height in common_sizes:
        thumbnail_url = f"{base_url}/v1/files/thumbnail/{file_id}?w={width}&h={height}"
        thumbnail_urls.append({
            "width": width,
            "height": height,
            "url": thumbnail_url
        })
    
    return thumbnail_urls 