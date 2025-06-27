from sqlalchemy import Column, Integer, String, ForeignKey, Table, BigInteger
from sqlalchemy.orm import relationship
from core.core.database import Base

class Role(Base):
    __tablename__ = "roles"
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    # Relationship
    users = relationship("UserRole", back_populates="role")

class UserRole(Base):
    __tablename__ = "user_roles"
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    role_id = Column(BigInteger, ForeignKey("roles.id"), nullable=False)
    # Relationship
    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="users") 