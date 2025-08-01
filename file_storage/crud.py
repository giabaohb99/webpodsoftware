from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import Optional
from fastapi import UploadFile, HTTPException, status

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