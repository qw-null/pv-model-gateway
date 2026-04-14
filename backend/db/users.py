# backend/db/users.py（新增部分）
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id          = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username    = Column(String(64), unique=True, nullable=False, index=True, comment="用户名")
    password    = Column(String(255), nullable=False, comment="bcrypt 哈希密码")
    nickname    = Column(String(64), nullable=True, comment="昵称")
    role        = Column(String(32), default="user", comment="角色：admin / user")
    is_active   = Column(Boolean, default=True, comment="是否启用")
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), onupdate=func.now())
