from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class StoryBase(BaseModel):
    title: str
    description: Optional[str] = None
    content: str
    tags: Optional[str] = None
    published: Optional[bool] = False

class StoryCreate(StoryBase):
    pass

class Story(StoryBase):
    id: int
    slug: str
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Use model_config for Pydantic v2
    model_config = ConfigDict(from_attributes=True)

class StoryPage(BaseModel):
    page: int
    limit: int
    total: int
    items: List[Story] 