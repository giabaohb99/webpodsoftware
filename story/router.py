from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from . import crud, schemas
from core.core.database import get_db
from core.core.auth import PermissionChecker, get_current_user
from users import models as users_models

router = APIRouter(
    prefix="/story",
    tags=["Story"]
)

# Define permissions for this endpoint
story_creator_permission = PermissionChecker(required_roles=["story_manager", "admin"])

@router.get("/", response_model=schemas.StoryPage, summary="[Admin] List stories")
def list_stories(
    db: Session = Depends(get_db),
    page: int = 1,
    limit: int = 20,
    keyword: Optional[str] = None,
    current_user: users_models.User = Depends(get_current_user)
):
    """
    [Admin] Retrieve stories with pagination and filtering. Requires authentication.
    """
    skip = (page - 1) * limit if page > 0 else 0
    stories, total = crud.get_stories(db, skip=skip, limit=limit, keyword=keyword)
    return {"page": page, "limit": limit, "total": total, "items": stories}

@router.get("/public/", response_model=schemas.StoryPage, summary="List public stories")
def list_public_stories(
    db: Session = Depends(get_db),
    page: int = 1,
    limit: int = 20,
    keyword: Optional[str] = None
):
    """
    Retrieve public stories with pagination and filtering.
    """
    skip = (page - 1) * limit if page > 0 else 0
    stories, total = crud.get_stories(db, skip=skip, limit=limit, keyword=keyword)
    return {"page": page, "limit": limit, "total": total, "items": stories}

@router.post("/create", response_model=schemas.Story, status_code=status.HTTP_201_CREATED)
def create_story(
    story: schemas.StoryCreate,
    db: Session = Depends(get_db),
    current_user: users_models.User = Depends(story_creator_permission)
):
    """
    Create a new story. Requires 'story_manager' or 'admin' role.
    """
    return crud.create_story(db=db, story=story, author_id=current_user.id)

@router.get("/{slug}", response_model=schemas.Story, summary="[Admin] Get story by slug")
def get_story(slug: str, db: Session = Depends(get_db), current_user: users_models.User = Depends(get_current_user)):
    """
    [Admin] Get a single story by its slug. Requires authentication.
    """
    db_story = crud.get_story_by_slug(db, slug=slug)
    if db_story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    return db_story

@router.get("/public/{slug}", response_model=schemas.Story, summary="Get public story by slug")
def get_public_story(slug: str, db: Session = Depends(get_db)):
    """
    Get a single public story by its slug.
    """
    db_story = crud.get_story_by_slug(db, slug=slug)
    if db_story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    return db_story