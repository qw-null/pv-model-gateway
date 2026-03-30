import asyncio
import time
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from typing import Callable
from config import settings

# 全局进程池（主进程生命周期内复用）
_pool: ProcessPoolExecutor = None


def get_pool() -> ProcessPoolExecutor:
    global _pool
    if _pool is None:
        _pool = ProcessPoolExecutor(max_workers=settings.WORKER_PROCESSES)
    return _pool


def _execute_model(model_path: str, inputs: dict) -> dict:
    """
    在子进程中执行模型。
    通过文件路径重新加载模块，避免跨进程传递不可序列化对象。
    """
    import importlib.util
    from pathlib import Path

    model_file = Path(model_path)
    spec = importlib.util.spec_from_file_location("_model_exec", model_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, "run"):
        raise AttributeError(f"模型文件 {model_path} 中未找到 run() 函数")

    return module.run(inputs)


async def safe_execute(model_path: str, inputs: dict, timeout: float = None) -> tuple[dict, float]:
    """
    异步安全执行模型，返回 (outputs, execution_time_ms)
    - 进程隔离：子进程崩溃不影响主进程
    - 超时控制：超时后强制取消
    """
    if timeout is None:
        timeout = settings.MODEL_TIMEOUT

    loop = asyncio.get_event_loop()
    start = time.monotonic()

    try:
        result = await asyncio.wait_for(
            loop.run_in_executor(
                get_pool(),
                partial(_execute_model, model_path, inputs)
            ),
            timeout=timeout
        )
        elapsed_ms = (time.monotonic() - start) * 1000
        return result, round(elapsed_ms, 2)

    except asyncio.TimeoutError:
        raise TimeoutError(f"模型执行超时（超过 {timeout}s），请检查模型逻辑或增大 timeout 配置")
    except Exception as e:
        raise RuntimeError(f"模型执行异常: {str(e)}")
