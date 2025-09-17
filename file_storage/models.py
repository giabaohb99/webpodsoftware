from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, UniqueConstraint, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.core.database import Base

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), index=True)
    file_url = Column(String(512), nullable=False)
    content_type = Column(String(100))
    file_extension = Column(String(20), index=True)
    size = Column(Float, comment="File size in bytes") # Using Float for size in bytes
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    thumbnails = relationship("Thumbnail", back_populates="original_file", cascade="all, delete-orphan")

    @property
    def download_url(self):
        return self.file_url

class Thumbnail(Base):
    __tablename__ = "thumbnails"

    id = Column(Integer, primary_key=True, index=True)
    original_file_id = Column(Integer, ForeignKey("files.id", ondelete="CASCADE"), nullable=False)
    
    # Size parameters
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    quality = Column(Integer, default=80)
    format = Column(String(10), default="webp")
    
    # Generated file info
    file_url = Column(String(512), nullable=False)
    file_size = Column(Float)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_accessed = Column(DateTime)
    access_count = Column(Integer, default=0)
    
    # Relationship
    original_file = relationship("File", back_populates="thumbnails")
    
    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint('original_file_id', 'width', 'height', 'format', 'quality', 
                        name='unique_thumbnail'),
        Index('idx_thumbnail_lookup', 'original_file_id', 'width', 'height', 'format', 'quality'),
    ) 