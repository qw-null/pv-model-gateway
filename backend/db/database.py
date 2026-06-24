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


# backend/db/database.py
# 在 init_db() 函数中，Base.metadata.create_all(bind=engine) 之后追加：

def _migrate_add_columns(engine):
    """
    安全地为已有表补充缺失列（幂等操作，列已存在时跳过）。
    替代 Alembic，适用于小型项目的轻量迁移。
    """
    migrations = [
        # (表名, 列名, 列定义SQL)
        ("inverters", "p_aco", "FLOAT NOT NULL DEFAULT 0.0 COMMENT 'Sandia Paco: 额定交流功率 W'"),
        ("inverters", "p_dco", "FLOAT NOT NULL DEFAULT 0.0 COMMENT 'Sandia Pdco: 额定直流功率 W'"),
        ("inverters", "p_so",  "FLOAT NOT NULL DEFAULT 0.0 COMMENT 'Sandia Pso: 启动自耗功率 W'"),
        ("inverters", "c_o",   "FLOAT NOT NULL DEFAULT 0.0 COMMENT 'Sandia Co: 二次修正系数 1/W'"),
    ]

    with engine.connect() as conn:
        for table, column, definition in migrations:
            # 查询该列是否已存在
            result = conn.execute(text(
                "SELECT COUNT(*) FROM information_schema.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND TABLE_NAME = :table AND COLUMN_NAME = :column"
            ), {"table": table, "column": column})
            exists = result.scalar()

            if not exists:
                conn.execute(text(
                    f"ALTER TABLE `{table}` ADD COLUMN `{column}` {definition}"
                ))
                conn.commit()
                import logging
                logging.getLogger("database").info(
                    f"[迁移] 表 {table} 新增列 {column} 成功"
                )


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
    _migrate_add_columns(engine)            # 新增：自动补列

    logger.info("数据库基础表结构初始化完成")

    # 运行迁移
    with engine.begin() as conn:
        try:
            _run_migrations(conn)
            logger.info("数据库迁移检查完成")
        except Exception as e:
            logger.error(f"数据库迁移失败: {e}")
            raise

