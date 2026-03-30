# db/models.py

from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    Text,
    JSON,
    ForeignKey,
)
from sqlalchemy.sql import func
from db.database import Base


class ModelRecord(Base):
    """
    模型主表
    """
    __tablename__ = "model_records"

    # ✅ 数据库主键（自增）
    id = Column(Integer, primary_key=True, autoincrement=True)

    # ✅ 逻辑唯一标识（代码层）
    name = Column(String(100), unique=True, nullable=False, index=True)

    title = Column(String(200), nullable=False)
    version = Column(String(20), default="1.0.0")
    description = Column(Text, default="")
    author = Column(String(100), default="")
    category = Column(String(100), default="未分类")

    meta_json = Column(JSON, nullable=False)

    is_active = Column(Boolean, default=True)
    call_count = Column(Integer, default=0)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )


class ModelRelation(Base):
    """
    模型关系表
    """
    __tablename__ = "model_relations"

    id = Column(Integer, primary_key=True, autoincrement=True)

    from_model_id = Column(
        Integer,
        ForeignKey("model_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    to_model_id = Column(
        Integer,
        ForeignKey("model_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # pre / post / depends_on / conflicts_with
    relation_type = Column(String(30), nullable=False)


class ExecutionLog(Base):
    """
    模型执行日志表
    """
    __tablename__ = "execution_logs"

    id = Column(Integer, primary_key=True, index=True)

    # ✅ 强关联到模型表
    model_record_id = Column(
        Integer,
        ForeignKey("model_records.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    model_name = Column(String(100), nullable=False)

    inputs = Column(JSON, nullable=False)
    outputs = Column(JSON, nullable=True)

    success = Column(Boolean, default=True)
    error_msg = Column(Text, nullable=True)

    execution_time_ms = Column(Float, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
