# backend/config.py
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()  # 自动读取同目录下的 .env 文件


BASE_DIR = Path(__file__).parent

class Settings:
    APP_TITLE: str = "PV Model Gateway"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "光伏模型网关 - 将光伏模型代码自动转化为 RESTful API 服务"

    # 模型目录
    MODELS_DIR: Path = BASE_DIR / "models_repo"

    # ✅ MySQL 数据库配置（通过环境变量注入）
    MYSQL_HOST:     str = os.getenv("MYSQL_HOST",     "localhost")
    MYSQL_PORT:     int = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER:     str = os.getenv("MYSQL_USER",     "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "123456")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "pv_gateway")

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
            f"?charset=utf8mb4"
        )

    # 执行引擎
    WORKER_PROCESSES: int = int(os.getenv("WORKER_PROCESSES", 4))
    MODEL_TIMEOUT:  float = float(os.getenv("MODEL_TIMEOUT",  30.0))

    # Redis 缓存（可选）
    REDIS_URL:    str  = os.getenv("REDIS_URL",    "")
    ENABLE_CACHE: bool = os.getenv("ENABLE_CACHE", "false").lower() == "true"

    # CORS
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")

settings = Settings()
