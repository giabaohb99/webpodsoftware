from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class StoryCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class StoryCategoryCreate(StoryCategoryBase):
    pass

class StoryCategory(StoryCategoryBase):
    id: int
    slug: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class StoryBase(BaseModel):
    title: str
    description: Optional[str] = None
    content: str
    tags: Optional[str] = None
    published: Optional[bool] = False
    category_id: Optional[int] = None
    story_type: Optional[str] = "article"

class StoryCreate(StoryBase):
    pass

class Story(StoryBase):
    id: int
    slug: str
    author_id: int
    category_id: Optional[int] = None
    story_type: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    category: Optional[StoryCategory] = None
    
    # Use model_config for Pydantic v2
    model_config = ConfigDict(from_attributes=True)

class StoryPage(BaseModel):
    page: int
    limit: int
    total: int
    items: List[Story] 