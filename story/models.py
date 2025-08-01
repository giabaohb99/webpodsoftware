from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.core.database import Base

class StoryCategory(Base):
    __tablename__ = "story_categories"
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    slug = Column(String(100), nullable=False, unique=True)
    description = Column(String(512), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Story(Base):
    __tablename__ = "stories"
    id = Column(BigInteger, primary_key=True, index=True)
    title = Column(String(255), unique=True, nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    description = Column(String(512), nullable=True)
    content = Column(Text, nullable=False)
    tags = Column(String(255), nullable=True)
    published = Column(Boolean, default=False)
    author_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    category_id = Column(BigInteger, ForeignKey("story_categories.id"), nullable=True)
    story_type = Column(String(50), nullable=False, default="article")  # article, report, recruitment
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    author = relationship("User")
    category = relationship("StoryCategory") 