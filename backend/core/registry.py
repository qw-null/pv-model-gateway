import importlib.util
import logging
from pathlib import Path
from typing import Optional
from config import settings

logger = logging.getLogger("registry")


class ModelRegistry:
    """
    模型注册表：扫描 models_repo 目录，加载所有合法模型。
    每个模型目录结构：
        models_repo/
            {model_name}/
                meta.py    ← 包含 MODEL_META 字典
                model.py   ← 包含 run(inputs) 函数
    """

    def __init__(self):
        self._registry: dict[str, dict] = {}  # {name: {meta, model_path, meta_path}}

    def scan(self) -> dict:
        """扫描并加载所有模型，返回注册表快照"""
        self._registry.clear()
        models_dir = settings.MODELS_DIR

        if not models_dir.exists():
            logger.warning(f"模型目录不存在: {models_dir}")
            return {}

        for model_dir in models_dir.iterdir():
            if not model_dir.is_dir():
                continue
            self._load_model_dir(model_dir)

        logger.info(f"模型扫描完成，共加载 {len(self._registry)} 个模型: {list(self._registry.keys())}")
        return dict(self._registry)

    def _load_model_dir(self, model_dir: Path):
        """加载单个模型目录"""
        meta_file = model_dir / "meta.py"
        model_file = model_dir / "model.py"

        if not meta_file.exists():
            logger.warning(f"跳过 {model_dir.name}：缺少 meta.py")
            return
        if not model_file.exists():
            logger.warning(f"跳过 {model_dir.name}：缺少 model.py")
            return

        try:
            meta = self._load_meta(meta_file)
            name = meta.get("name")
            if not name:
                logger.error(f"跳过 {model_dir.name}：MODEL_META 缺少 'name' 字段")
                return

            self._registry[name] = {
                "meta": meta,
                "model_path": str(model_file),
                "meta_path": str(meta_file),
                "dir": str(model_dir),
            }
            logger.info(f"已加载模型: {name} ({meta.get('title', '')})")

        except Exception as e:
            logger.error(f"加载模型 {model_dir.name} 失败: {e}")

    def _load_meta(self, meta_file: Path) -> dict:
        """动态加载 meta.py，提取 MODEL_META"""
        spec = importlib.util.spec_from_file_location("_meta_loader", meta_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if not hasattr(module, "MODEL_META"):
            raise AttributeError(f"{meta_file} 中未找到 MODEL_META")

        return module.MODEL_META

    def get(self, name: str) -> Optional[dict]:
        return self._registry.get(name)

    def all(self) -> dict:
        return dict(self._registry)

    def names(self) -> list:
        return list(self._registry.keys())

    def reload(self, name: str = None):
        """热重载：重新扫描全部或指定模型"""
        if name:
            entry = self._registry.get(name)
            if entry:
                self._load_model_dir(Path(entry["dir"]))
        else:
            self.scan()


# 全局单例
registry = ModelRegistry()
