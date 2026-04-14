# backend/app.py

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from db.database import init_db, check_db_connection, SessionLocal
from db.models import ModelRecord
from db.users import User                          # ← 新增
from core.registry import registry
from core.auth import hash_password                # ← 新增
from api.model_routes import router as model_router
from api.execute_routes import router as execute_router
from api.auth_routes import router as auth_router  # ← 新增

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("app")


# ─────────────────────────────────────────────
# 同步 registry 到数据库（保持原有逻辑不变）
# ─────────────────────────────────────────────

def _sync_registry_to_db(loaded: dict):
    """将 registry 中扫描到的模型同步到数据库，基于逻辑唯一标识 name"""
    db = SessionLocal()
    try:
        for name, entry in loaded.items():
            meta = entry["meta"]
            record = db.query(ModelRecord).filter(
                ModelRecord.name == name
            ).first()

            if record:
                record.title       = meta.get("title", name)
                record.version     = meta.get("version", "1.0.0")
                record.description = meta.get("description", "")
                record.author      = meta.get("author", "")
                record.category    = meta.get("category", "未分类")
                record.meta_json   = meta
                record.is_active   = True
            else:
                record = ModelRecord(
                    name=name,
                    title=meta.get("title", name),
                    version=meta.get("version", "1.0.0"),
                    description=meta.get("description", ""),
                    author=meta.get("author", ""),
                    category=meta.get("category", "未分类"),
                    meta_json=meta,
                )
                db.add(record)

        db.commit()
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


# ─────────────────────────────────────────────
# ✅ 新增：初始化默认管理员账号
# ─────────────────────────────────────────────

def _init_admin():
    """首次启动时创建默认管理员账号，已存在则跳过"""
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == "admin").first():
            db.add(User(
                username="admin",
                password=hash_password("admin123"),
                nickname="管理员",
                role="admin",
            ))
            db.commit()
            logger.info("默认管理员账号已创建（admin / admin123），请尽快修改密码")
        else:
            logger.info("管理员账号已存在，跳过初始化")
    except Exception as e:
        db.rollback()
        logger.error(f"初始化管理员账号失败: {e}")
        raise
    finally:
        db.close()


# ─────────────────────────────────────────────
# 生命周期管理
# ─────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── 启动 ─────────────────────────────
    logger.info("检查数据库连接...")
    if not check_db_connection():
        raise RuntimeError(
            f"无法连接到数据库: "
            f"{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}"
        )

    logger.info("初始化数据库表结构...")
    init_db()

    logger.info("扫描并加载模型...")
    loaded = registry.scan()
    logger.info(f"已加载模型: {list(loaded.keys())}")
    _sync_registry_to_db(loaded)

    logger.info("初始化管理员账号...")  # ← 新增
    _init_admin()                       # ← 新增

    logger.info("PV Model Gateway 启动完成 ✅")
    yield

    # ── 关闭 ─────────────────────────────
    logger.info("正在关闭进程池...")
    from core.executor import get_pool
    get_pool().shutdown(wait=False)
    logger.info("PV Model Gateway 已关闭")


# ─────────────────────────────────────────────
# 应用创建
# ─────────────────────────────────────────────

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_TITLE,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router)    # ← 新增，放在最前确保 /api/auth/* 优先注册
    app.include_router(model_router)
    app.include_router(execute_router)

    @app.get("/", summary="服务健康检查")
    def health_check():
        return {
            "status": "ok",
            "app": settings.APP_TITLE,
            "version": settings.APP_VERSION,
            "loaded_models": registry.names(),
            "db_connected": check_db_connection(),
        }

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        lifespan="on",
    )
