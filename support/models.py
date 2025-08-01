from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.core.database import Base

class Support(Base):
    __tablename__ = "supports"
    id = Column(BigInteger, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    email = Column(String(255), nullable=False)  # Email của người gửi support
    fullname = Column(String(255), nullable=True)  # Tên đầy đủ của người gửi
    support_type = Column(String(50), nullable=False)  # general, recruitment, technical
    source_type = Column(String(50), nullable=True)  # story, user, etc.
    source_id = Column(BigInteger, nullable=True)  # ID của source
    file_ids = Column(Text, nullable=True)  # Lưu dạng "1,456,233,55"
    status = Column(String(50), default="pending")  # pending, in_progress, resolved
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 