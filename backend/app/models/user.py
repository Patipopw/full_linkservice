from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from app.models.base import Base
from app.models.auth import user_roles
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    nickname = Column(String, nullable=True)
    tel = Column(String, nullable=True)
    position = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True), nullable=True) 

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),  onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)


    roles = relationship("Role", secondary=user_roles, back_populates="users")