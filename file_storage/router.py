from fastapi import APIRouter, Depends, UploadFile, File as FastAPIFile, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from core.core.database import get_db
from core.core.storage import s3_storage
from core.core import auth as core_auth
from users import schemas as users_schemas
from . import crud, schemas

router = APIRouter(
    prefix="/files",
    tags=["files"],
    responses={404: {"description": "Not found"}},
)

# --- Private (Admin) Endpoints ---

@router.post("/upload", response_model=schemas.File, dependencies=[Depends(core_auth.get_current_user)])
def upload_file(
    db: Session = Depends(get_db), 
    file: UploadFile = FastAPIFile(...)
):
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

    db_file = crud.create_file(db=db, file=file_data)
    return db_file

@router.get("/", response_model=schemas.FileList)
def get_file_list(
    db: Session = Depends(get_db),
    keyword: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    file_extension: Optional[str] = None,
    ids: Optional[str] = Query(None),
    page: int = 1,
    limit: int = 100,
    current_user: users_schemas.User = Depends(core_auth.get_current_user)
):
    skip = (page - 1) * limit

    file_ids_list: Optional[List[int]] = None
    if ids:
        try:
            file_ids_list = [int(id_str.strip()) for id_str in ids.split(',')]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid 'ids' format. Must be a comma-separated list of integers.")

    result = crud.get_files(
        db=db, keyword=keyword, start_date=start_date, end_date=end_date,
        file_extension=file_extension, file_ids=file_ids_list, skip=skip, limit=limit
    )
    return {"page": page, "limit": limit, "total": result["total"], "items": result["files"]}

@router.get("/{file_id}", response_model=schemas.File)
def get_file_detail(
    file_id: int, 
    db: Session = Depends(get_db),
    current_user: users_schemas.User = Depends(core_auth.get_current_user)
):
    db_file = crud.get_file(db, file_id=file_id)
    if db_file is None:
        raise HTTPException(status_code=404, detail="File not found")
    return db_file

# --- Public Endpoints ---

@router.get("/public/", response_model=schemas.FileList)
def get_public_file_list(
    db: Session = Depends(get_db),
    keyword: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    file_extension: Optional[str] = None,
    ids: Optional[str] = Query(None),
    page: int = 1,
    limit: int = 100
):
    skip = (page - 1) * limit
    
    file_ids_list: Optional[List[int]] = None
    if ids:
        try:
            file_ids_list = [int(id_str.strip()) for id_str in ids.split(',')]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid 'ids' format. Must be a comma-separated list of integers.")
            
    result = crud.get_files(
        db=db, keyword=keyword, start_date=start_date, end_date=end_date,
        file_extension=file_extension, file_ids=file_ids_list, skip=skip, limit=limit,
        content_type_prefix="image" # <--- Public can only see images
    )
    return {"page": page, "limit": limit, "total": result["total"], "items": result["files"]}

@router.get("/public/{file_id}", response_model=schemas.File)
def get_public_file_detail(file_id: int, db: Session = Depends(get_db)):
    db_file = crud.get_file(db, file_id=file_id)
    if db_file is None:
        raise HTTPException(status_code=404, detail="File not found")
    return db_file 