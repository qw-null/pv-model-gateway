# backend/db/database.py

import logging
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

logger = logging.getLogger("database")

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
    echo=False,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# ─────────────────────────────────────────────
# Session 依赖
# ─────────────────────────────────────────────

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─────────────────────────────────────────────
# 迁移逻辑
# ─────────────────────────────────────────────

def _get_existing_tables(conn):
    inspector = inspect(conn)
    return inspector.get_table_names()


def _create_model_relations_table(conn):
    """
    创建模型关系表（如果不存在）
    """

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS model_relations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            from_model_id INT NOT NULL,
            to_model_id INT NOT NULL,
            relation_type VARCHAR(30) NOT NULL,

            FOREIGN KEY (from_model_id)
                REFERENCES model_records(id)
                ON DELETE CASCADE,

            FOREIGN KEY (to_model_id)
                REFERENCES model_records(id)
                ON DELETE CASCADE,

            UNIQUE KEY uniq_relation (
                from_model_id,
                to_model_id,
                relation_type
            ),

            INDEX idx_from (from_model_id),
            INDEX idx_to (to_model_id)
        )
    """))

    logger.info("model_relations 表检查完成")


def _run_migrations(conn):
    tables = _get_existing_tables(conn)

    if "model_records" in tables:
        _create_model_relations_table(conn)


# ─────────────────────────────────────────────
# 初始化数据库
# ─────────────────────────────────────────────

def init_db():
    """
    初始化数据库结构
    """

    from db.models import ModelRecord, ModelRelation, ExecutionLog

    # 创建 ORM 定义的表
    Base.metadata.create_all(bind=engine)

    logger.info("数据库基础表结构初始化完成")

    # 运行迁移
    with engine.begin() as conn:
        try:
            _run_migrations(conn)
            logger.info("数据库迁移检查完成")
        except Exception as e:
            logger.error(f"数据库迁移失败: {e}")
            raise


# ─────────────────────────────────────────────
# 健康检查
# ─────────────────────────────────────────────

def check_db_connection() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
