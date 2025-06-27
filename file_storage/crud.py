from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import Optional

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