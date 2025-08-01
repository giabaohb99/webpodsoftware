from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional, List

from . import crud, schemas
from core.core.database import get_db
from core.core.auth import PermissionChecker, get_current_user
from users import models as users_models

router = APIRouter(
    prefix="/support",
    tags=["Support"]
)

# Define permissions
support_creator_permission = PermissionChecker(required_roles=["user", "admin"])
support_admin_permission = PermissionChecker(required_roles=["admin"])
support_manager_permission = PermissionChecker(required_roles=["support_manager", "admin"])

# Public endpoints (no authentication required)
@router.post("/public/", response_model=schemas.SupportResponse, status_code=status.HTTP_201_CREATED)
async def create_public_support(
    support: schemas.SupportCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new support request (public - no authentication required).
    """
    return await crud.create_support_with_notifications(
        db=db, 
        support_in=support
    )

@router.get("/public/", response_model=schemas.SupportPage)
def list_public_supports(
    db: Session = Depends(get_db),
    page: int = 1,
    limit: int = 20,
    keyword: Optional[str] = None,
    support_type: Optional[str] = None,
    status: Optional[str] = None
):
    """
    List public support requests (no authentication required).
    """
    skip = (page - 1) * limit if page > 0 else 0
    
    supports, total = crud.get_supports(
        db, 
        skip=skip, 
        limit=limit, 
        keyword=keyword,
        support_type=support_type,
        status=status
    )
    
    return {"page": page, "limit": limit, "total": total, "items": supports}

@router.get("/public/{support_id}", response_model=schemas.Support)
def get_public_support(
    support_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific support request (public - no authentication required).
    """
    support = crud.get_support_by_id(db, support_id)
    if not support:
        raise HTTPException(status_code=404, detail="Support request not found")
    
    return support

@router.post("/public/recruitment/{story_id}", response_model=schemas.Support, status_code=status.HTTP_201_CREATED)
async def create_public_recruitment_application(
    story_id: int,
    support: schemas.SupportCreate,
    db: Session = Depends(get_db)
):
    """
    Create a recruitment application for a specific story (public - no authentication required).
    """
    # Verify story exists and is a recruitment type
    from story.crud import get_story_by_id
    story = get_story_by_id(db, story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    if story.story_type != "recruitment":
        raise HTTPException(status_code=400, detail="This story is not a recruitment post")
    
    # Set source information
    support.source_type = "story"
    support.source_id = story_id
    support.support_type = "recruitment"
    
    return await crud.create_support_with_notifications(
        db=db, 
        support_in=support
    )

# Protected endpoints (require authentication)
@router.post("/", response_model=schemas.Support, status_code=status.HTTP_201_CREATED)
async def create_support(
    support: schemas.SupportCreate,
    db: Session = Depends(get_db),
    current_user: users_models.User = Depends(support_creator_permission)
):
    """
    Create a new support request. Requires authentication.
    """
    return await crud.create_support_with_notifications(
        db=db, 
        support_in=support
    )

@router.get("/", response_model=schemas.SupportPage)
def list_supports(
    db: Session = Depends(get_db),
    page: int = 1,
    limit: int = 20,
    keyword: Optional[str] = None,
    support_type: Optional[str] = None,
    status: Optional[str] = None,
    current_user: users_models.User = Depends(get_current_user)
):
    """
    List support requests with filtering. Users can only see their own requests.
    Admins and support managers can see all requests.
    """
    skip = (page - 1) * limit if page > 0 else 0
    
    # If user is not admin or support manager, only show their own supports
    email_filter = None if "admin" in current_user.roles or "support_manager" in current_user.roles else current_user.username
    
    supports, total = crud.get_supports(
        db, 
        skip=skip, 
        limit=limit, 
        keyword=keyword,
        support_type=support_type,
        status=status,
        email=email_filter
    )
    
    return {"page": page, "limit": limit, "total": total, "items": supports}

@router.get("/{support_id}", response_model=schemas.Support)
def get_support(
    support_id: int,
    db: Session = Depends(get_db),
    current_user: users_models.User = Depends(get_current_user)
):
    """
    Get a specific support request. Users can only see their own requests.
    Admins and support managers can see all requests.
    """
    support = crud.get_support_by_id(db, support_id)
    if not support:
        raise HTTPException(status_code=404, detail="Support request not found")
    
    # Check if user can access this support
    if "admin" not in current_user.roles and "support_manager" not in current_user.roles and support.email != current_user.username:
        raise HTTPException(status_code=403, detail="Not authorized to view this support request")
    
    return support

@router.put("/{support_id}", response_model=schemas.Support)
def update_support(
    support_id: int,
    support_update: schemas.SupportUpdate,
    db: Session = Depends(get_db),
    current_user: users_models.User = Depends(support_admin_permission)
):
    """
    Update a support request. Only admins can update all fields.
    """
    support = crud.update_support(db, support_id, support_update)
    if not support:
        raise HTTPException(status_code=404, detail="Support request not found")
    
    return support

@router.patch("/{support_id}/status", response_model=schemas.Support)
async def update_support_status(
    support_id: int,
    status_update: schemas.SupportStatusUpdate,
    db: Session = Depends(get_db),
    current_user: users_models.User = Depends(support_manager_permission)
):
    """
    Update support status. Support managers and admins can update status.
    """
    support = await crud.update_support_status(db, support_id, status_update.status, status_update.note)
    if not support:
        raise HTTPException(status_code=404, detail="Support request not found")
    
    return support

@router.delete("/{support_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_support(
    support_id: int,
    db: Session = Depends(get_db),
    current_user: users_models.User = Depends(support_admin_permission)
):
    """
    Delete a support request. Only admins can delete.
    """
    success = crud.delete_support(db, support_id)
    if not success:
        raise HTTPException(status_code=404, detail="Support request not found")

@router.get("/source/{source_type}/{source_id}", response_model=List[schemas.Support])
def get_supports_by_source(
    source_type: str,
    source_id: int,
    db: Session = Depends(get_db),
    current_user: users_models.User = Depends(support_manager_permission)
):
    """
    Get all support requests related to a specific source. Support managers and admins can access.
    """
    supports = crud.get_supports_by_source(db, source_type, source_id)
    return supports

@router.post("/recruitment/{story_id}", response_model=schemas.Support, status_code=status.HTTP_201_CREATED)
async def create_recruitment_application(
    story_id: int,
    support: schemas.SupportCreate,
    db: Session = Depends(get_db),
    current_user: users_models.User = Depends(support_creator_permission)
):
    """
    Create a recruitment application for a specific story.
    """
    # Verify story exists and is a recruitment type
    from story.crud import get_story_by_id
    story = get_story_by_id(db, story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    if story.story_type != "recruitment":
        raise HTTPException(status_code=400, detail="This story is not a recruitment post")
    
    # Set source information
    support.source_type = "story"
    support.source_id = story_id
    support.support_type = "recruitment"
    
    return await crud.create_support_with_notifications(
        db=db, 
        support_in=support
    ) 