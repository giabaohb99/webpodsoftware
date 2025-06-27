from sqlalchemy.orm import Session
from story.models import Story
from story.schemas import StoryCreate
from users.models import User
import re
from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from slugify import slugify
import uuid
from sqlalchemy import or_

def slugify(title: str) -> str:
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title).lower()
    slug = re.sub(r'\s+', '-', slug).strip('-')
    return slug

def create_story(db: Session, story_in: StoryCreate, author_id: int) -> Story:
    # Check for existing title first
    existing_story_by_title = db.query(Story).filter(Story.title == story_in.title).first()
    if existing_story_by_title:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Story with title already exists."
        )

    # Generate a unique slug
    base_slug = slugify(story_in.title)
    unique_slug = base_slug
    while db.query(Story).filter(Story.slug == unique_slug).first():
        unique_slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"

    db_story = Story(
        title=story_in.title,
        slug=unique_slug,
        description=story_in.description,
        content=story_in.content,
        tags=story_in.tags,
        published=story_in.published,
        author_id=author_id
    )
    
    db.add(db_story)
    
    try:
        db.commit()
        db.refresh(db_story)
    except IntegrityError:
        db.rollback()
        # This handles race conditions where a duplicate was created
        # between the initial check and this commit.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A story with a conflicting title or slug was created just now. Please try again."
        )
        
    return db_story

def get_stories(db: Session, skip: int = 0, limit: int = 20, keyword: Optional[str] = None):
    """
    Retrieve stories with pagination and filtering.
    Returns a tuple of (list of stories, total count).
    """
    query = db.query(Story)

    if keyword:
        # Case-insensitive search in title, description, and tags
        search_filter = or_(
            Story.title.ilike(f"%{keyword}%"),
            Story.description.ilike(f"%{keyword}%"),
            Story.tags.ilike(f"%{keyword}%")
        )
        query = query.filter(search_filter)

    total = query.count()  # Get total count before pagination

    stories = query.order_by(Story.created_at.desc()).offset(skip).limit(limit).all()
    
    return stories, total

def get_story_by_id(db: Session, story_id: int) -> Story:
    return db.query(Story).filter_by(id=story_id).first()

def get_story_by_slug(db: Session, slug: str):
    return db.query(Story).filter(Story.slug == slug).first() 