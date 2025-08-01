from sqlalchemy.orm import Session
from story.models import Story, StoryCategory
from story.schemas import StoryCreate, StoryCategoryCreate
from users.models import User
import re
from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from slugify import slugify
import uuid
from sqlalchemy import or_
from core.core.email_service import email_service

def slugify_title(title: str) -> str:
    """Generate a URL-friendly slug from title"""
    return slugify(title)

def create_story(db: Session, story_in: StoryCreate, author_id: int) -> Story:
    """
    Create a new story with unique slug
    """
    # Generate base slug
    base_slug = slugify_title(story_in.title)
    unique_slug = base_slug
    
    # Ensure slug uniqueness
    counter = 1
    while db.query(Story).filter(Story.slug == unique_slug).first():
        unique_slug = f"{base_slug}-{counter}"
        counter += 1
    
    db_story = Story(
        title=story_in.title,
        slug=unique_slug,
        description=story_in.description,
        content=story_in.content,
        tags=story_in.tags,
        published=story_in.published,
        author_id=author_id,
        category_id=story_in.category_id,
        story_type=story_in.story_type or "article"
    )
    
    db.add(db_story)
    db.commit()
    db.refresh(db_story)
    
    return db_story

async def create_story_with_notifications(db: Session, story_in: StoryCreate, author_id: int) -> Story:
    """
    Create story and send notifications if it's a recruitment post
    """
    story = create_story(db, story_in, author_id)
    
    # If this is a recruitment story, send notification to admin
    if story.story_type == "recruitment":
        author = db.query(User).filter(User.id == author_id).first()
        author_name = author.name if author else "Unknown"
        
        # Extract requirements from content if possible
        story_requirements = None
        story_description = None
        
        if story_in.content:
            # Simple extraction of requirements (you can improve this)
            if "Yêu cầu:" in story_in.content:
                requirements_start = story_in.content.find("Yêu cầu:")
                requirements_end = story_in.content.find("</ul>", requirements_start)
                if requirements_end > requirements_start:
                    story_requirements = story_in.content[requirements_start:requirements_end+5]
            
            # Extract description
            if "Mô tả công việc" in story_in.content:
                desc_start = story_in.content.find("Mô tả công việc")
                desc_end = story_in.content.find("</p>", desc_start)
                if desc_end > desc_start:
                    story_description = story_in.content[desc_start:desc_end+4]
        
        await email_service.send_recruitment_notification(
            story_title=story.title,
            author_name=author_name,
            story_description=story_description,
            story_requirements=story_requirements
        )
    
    return story

def get_stories(db: Session, skip: int = 0, limit: int = 20, keyword: Optional[str] = None,
                story_type: Optional[str] = None, category_id: Optional[int] = None):
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
    
    if story_type:
        query = query.filter(Story.story_type == story_type)
    
    if category_id:
        query = query.filter(Story.category_id == category_id)
    
    total = query.count()  # Get total count before pagination
    
    stories = query.order_by(Story.created_at.desc()).offset(skip).limit(limit).all()
    
    return stories, total

def get_story_by_id(db: Session, story_id: int) -> Optional[Story]:
    return db.query(Story).filter(Story.id == story_id).first()

def get_story_by_slug(db: Session, slug: str) -> Optional[Story]:
    return db.query(Story).filter(Story.slug == slug).first()

# Category CRUD functions
def create_category(db: Session, category_in: StoryCategoryCreate) -> StoryCategory:
    # Check for existing name
    existing_category = db.query(StoryCategory).filter(StoryCategory.name == category_in.name).first()
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category with this name already exists."
        )
    
    # Generate slug
    base_slug = slugify(category_in.name)
    unique_slug = base_slug
    while db.query(StoryCategory).filter(StoryCategory.slug == unique_slug).first():
        unique_slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"
    
    db_category = StoryCategory(
        name=category_in.name,
        slug=unique_slug,
        description=category_in.description
    )
    
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    return db_category

def get_categories(db: Session) -> List[StoryCategory]:
    return db.query(StoryCategory).order_by(StoryCategory.name).all()

def get_category_by_id(db: Session, category_id: int) -> Optional[StoryCategory]:
    return db.query(StoryCategory).filter(StoryCategory.id == category_id).first() 