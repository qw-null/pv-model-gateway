# backend/app.py

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from db.database import init_db, check_db_connection, SessionLocal
from db.models import ModelRecord
from db.panel import PVPanel                              # ← 新增
from db.users import User
from core.registry import registry
from core.auth import hash_password
from core.pan_parser import parse_pan                     # ← 新增
from api.model_routes import router as model_router
from api.execute_routes import router as execute_router
from api.auth_routes import router as auth_router
from api.panel_routes import router as panel_router
from db.inverter import Inverter
from core.ond_parser import parse_ond
from api.inverter_routes import router as inverter_router

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
            meta   = entry["meta"]
            record = db.query(ModelRecord).filter(ModelRecord.name == name).first()

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
# ✅ 新增：同步 panels_repo 到数据库
# ─────────────────────────────────────────────

def _sync_panels_to_db():
    """
    扫描 panels_repo 目录下所有 .pan 文件：
    - 数据库中已存在（按 filename 匹配）→ 跳过
    - 数据库中不存在 → 解析后写入
    与 _sync_registry_to_db 逻辑保持一致
    """
    panels_dir = Path(getattr(settings, "PANELS_DIR", "panels_repo"))

    if not panels_dir.exists():
        logger.warning(f"panels_repo 目录不存在，跳过组件同步: {panels_dir}")
        return

    pan_files = [f for f in panels_dir.iterdir() if f.suffix.lower() == ".pan"]
    if not pan_files:
        logger.info("panels_repo 目录中无 .pan 文件，跳过同步")
        return

    db = SessionLocal()
    added   = 0
    skipped = 0

    try:
        for pan_file in pan_files:
            filename = pan_file.name

            # 按文件名判断是否已入库
            existing = db.query(PVPanel).filter(
                PVPanel.filename == filename
            ).first()

            if existing:
                skipped += 1
                continue

            # 读取并解析 .pan 文件
            try:
                try:
                    content = pan_file.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    content = pan_file.read_text(encoding="latin-1")

                parsed = parse_pan(content)

                panel = PVPanel(
                    filename    = filename,
                    file_path   = str(pan_file.resolve()),
                    raw_content = content,
                    **parsed,
                )
                db.add(panel)
                added += 1
                logger.info(f"已同步组件文件: {filename}")

            except Exception as e:
                logger.error(f"解析 .pan 文件失败，跳过: {filename} — {e}")
                continue

        db.commit()
        logger.info(f"组件同步完成：新增 {added} 个，跳过 {skipped} 个（已存在）")

    except Exception as e:
        db.rollback()
        logger.error(f"组件同步失败: {e}")
        raise
    finally:
        db.close()

# ─────────────────────────────────────────────
# ✅ 新增：同步 inverters_repo 到数据库
# ─────────────────────────────────────────────

def _sync_inverters_to_db():
    """扫描 inverters_repo 目录，将未入库的 .ond 文件同步到数据库"""
    inverters_dir = Path(getattr(settings, "INVERTERS_DIR", "inverters_repo"))

    if not inverters_dir.exists():
        logger.warning(f"inverters_repo 目录不存在，跳过逆变器同步: {inverters_dir}")
        return

    ond_files = list(inverters_dir.glob("*.[Oo][Nn][Dd]"))
    if not ond_files:
        logger.info("inverters_repo 目录中无 .ond 文件，跳过同步")
        return

    db = SessionLocal()
    added = skipped = 0
    try:
        for ond_file in ond_files:
            filename = ond_file.name
            if db.query(Inverter).filter(Inverter.filename == filename).first():
                skipped += 1
                continue
            try:
                try:
                    content = ond_file.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    content = ond_file.read_text(encoding="latin-1")

                parsed = parse_ond(content)
                db.add(Inverter(
                    filename    = filename,
                    file_path   = str(ond_file.resolve()),
                    raw_content = content,
                    **parsed,
                ))
                added += 1
                logger.info(f"已同步逆变器文件: {filename}")
            except Exception as e:
                logger.error(f"解析 .ond 文件失败，跳过: {filename} — {e}")

        db.commit()
        logger.info(f"逆变器同步完成：新增 {added} 个，跳过 {skipped} 个（已存在）")
    except Exception as e:
        db.rollback()
        logger.error(f"逆变器同步失败: {e}")
        raise
    finally:
        db.close()



# ─────────────────────────────────────────────
# 初始化默认管理员账号
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

    logger.info("同步 panels_repo 组件文件...")   # ← 新增
    _sync_panels_to_db()                          # ← 新增

    logger.info("同步 inverters_repo 逆变器文件...")
    _sync_inverters_to_db()

    logger.info("初始化管理员账号...")
    _init_admin()

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

    app.include_router(auth_router)
    app.include_router(model_router)
    app.include_router(execute_router)
    app.include_router(panel_router)              # ← 确认已注册
    app.include_router(inverter_router)            # ← 确认已注册

    @app.get("/", summary="服务健康检查")
    def health_check():
        return {
            "status":        "ok",
            "app":           settings.APP_TITLE,
            "version":       settings.APP_VERSION,
            "loaded_models": registry.names(),
            "db_connected":  check_db_connection(),
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
