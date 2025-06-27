from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.sql import func
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