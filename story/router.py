from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from . import crud, schemas
from core.core.database import get_db
from core.core.auth import PermissionChecker
from users import models as users_models

router = APIRouter(
    prefix="/story",
    tags=["Story"]
)

# Define permissions for this endpoint
# This instance will be used as a dependency
story_creator_permission = PermissionChecker(required_roles=["story_manager", "admin"])

@router.get("/", response_model=schemas.StoryPage, summary="List stories with pagination and filtering")
def list_stories(
    db: Session = Depends(get_db),
    page: int = 1,
    limit: int = 20,
    keyword: Optional[str] = None
):
    """
    Retrieve a list of stories with pagination and filtering.

    - **page**: The page number to retrieve (starts from 1).
    - **limit**: The number of items per page.
    - **keyword**: An optional keyword to search for in story titles, descriptions, and tags.
    """
    if page < 1:
        page = 1
    if limit < 1:
        limit = 1
        
    skip = (page - 1) * limit
    
    stories, total = crud.get_stories(db, skip=skip, limit=limit, keyword=keyword)
    
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "items": stories
    }

@router.post("/create", response_model=schemas.Story, status_code=status.HTTP_201_CREATED)
def create_story(
    story: schemas.StoryCreate, 
    db: Session = Depends(get_db),
    # Here, FastAPI will execute PermissionChecker, which in turn executes get_current_user
    # If all checks pass, the user object is returned and assigned to current_user
    current_user: users_models.User = Depends(story_creator_permission)
):
    """
    Create a new story.
    Requires user to have 'story_manager' or 'admin' role.
    """
    return crud.create_story(db=db, story=story, author_id=current_user.id)

@router.get("/{slug}", response_model=schemas.Story)
def get_story(slug: str, db: Session = Depends(get_db)):
    """
    Get a single story by its slug.
    This is a public endpoint.
    """
    db_story = crud.get_story_by_slug(db, slug=slug)
    if db_story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    return db_story 