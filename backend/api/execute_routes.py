# backend/api/execute_routes.py

import time
import json
import math
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import ModelRecord, ExecutionLog
from core.registry import registry
from core.executor import safe_execute

router = APIRouter(prefix="/api/run", tags=["模型执行"])


# ─────────────────────────────────────────────
# 工具函数：JSON 清洗
# ─────────────────────────────────────────────

def _sanitize_for_json(obj):
    """
    递归清洗数据，将 NaN / Infinity 替换为 None，
    确保 JSON 可序列化并可写入数据库。
    """
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj

    if isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [_sanitize_for_json(i) for i in obj]

    return obj


# ─────────────────────────────────────────────
# 主接口：执行模型（基于逻辑唯一标识 name）
# ─────────────────────────────────────────────

@router.post("/{name}", summary="执行指定模型")
async def run_model(
    name: str,
    body: dict,
    db: Session = Depends(get_db)
):
    """
    执行指定模型：
    - name 为模型逻辑唯一标识（MODEL_META.name）
    - body 为模型输入参数
    """

    # 1️⃣ 从 registry 查找模型
    entry = registry.get(name)
    if not entry:
        raise HTTPException(status_code=404, detail=f"模型 '{name}' 未注册或不存在")

    meta = entry["meta"]
    model_path = entry["model_path"]

    # 2️⃣ 输入参数校验
    input_errors = _validate_inputs(body, meta.get("inputs", []))
    if input_errors:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "输入参数校验失败",
                "errors": input_errors
            }
        )

    # 3️⃣ 执行模型
    timeout = meta.get("execution", {}).get("timeout")

    try:
        outputs, elapsed_ms = await safe_execute(
            model_path,
            body,
            timeout=timeout
        )
    except (TimeoutError, RuntimeError) as e:
        _log_execution(
            db=db,
            model_name=name,
            inputs=body,
            outputs=None,
            success=False,
            error_msg=str(e),
            elapsed_ms=0
        )
        raise HTTPException(status_code=500, detail=str(e))

    # 4️⃣ 清洗输出
    safe_outputs = _sanitize_for_json(outputs)

    # 5️⃣ 写执行日志
    _log_execution(
        db=db,
        model_name=name,
        inputs=body,
        outputs=safe_outputs,
        success=True,
        error_msg=None,
        elapsed_ms=elapsed_ms
    )

    # 6️⃣ 更新调用统计
    _update_call_count(db, name)

    # 7️⃣ 返回结果
    return {
        "success": True,
        "model": name,
        "version": meta.get("version", ""),
        "outputs": safe_outputs,
        "execution_time_ms": elapsed_ms,
    }


# ─────────────────────────────────────────────
# 输入参数校验
# ─────────────────────────────────────────────

def _validate_inputs(body: dict, input_defs: list) -> list:
    """
    根据 MODEL_META.inputs 定义校验请求参数
    """
    errors = []

    type_map = {
        "float": float,
        "int": int,
        "str": str,
        "bool": bool,
        "list": list,
        "dict": dict,
    }

    for inp in input_defs:
        name = inp["name"]
        required = inp.get("required", True)
        expected = inp.get("type", "str")

        if name not in body:
            if required:
                errors.append(f"缺少必填参数: '{name}'")
            continue

        val = body[name]

        # 字符串必填校验
        if expected == "str" and required and (val is None or str(val).strip() == ""):
            errors.append(f"参数 '{name}' 不能为空字符串")
            continue

        # 类型校验 & 自动转换
        py_type = type_map.get(expected)
        if py_type and not isinstance(val, py_type):
            try:
                body[name] = py_type(val)
            except (ValueError, TypeError):
                errors.append(
                    f"参数 '{name}' 类型错误，期望 {expected}，"
                    f"实际传入: {type(val).__name__}"
                )
                continue

        # 枚举校验
        if expected == "enum" and "options" in inp:
            if val not in inp["options"]:
                errors.append(
                    f"参数 '{name}' 值不合法，允许值: {inp['options']}"
                )

        # 数值范围校验
        if expected in ("float", "int"):
            cur = body.get(name)
            if cur is None:
                continue

            if "min" in inp and cur < inp["min"]:
                errors.append(f"参数 '{name}' 不能小于 {inp['min']}")

            if "max" in inp and cur > inp["max"]:
                errors.append(f"参数 '{name}' 不能大于 {inp['max']}")

    return errors


# ─────────────────────────────────────────────
# 执行日志
# ─────────────────────────────────────────────

def _log_execution(
    db: Session,
    model_name: str,
    inputs: dict,
    outputs: dict,
    success: bool,
    error_msg: str,
    elapsed_ms: float
):
    """
    写入执行日志（不影响主流程）
    """
    try:
        log = ExecutionLog(
            model_name=model_name,
            inputs=inputs,
            outputs=outputs,
            success=success,
            error_msg=error_msg,
            execution_time_ms=elapsed_ms,
        )
        db.add(log)
        db.commit()
    except Exception as e:
        db.rollback()
        import logging
        logging.getLogger("execute_routes").error(
            f"写入执行日志失败: {e}"
        )


# ─────────────────────────────────────────────
# 调用统计
# ─────────────────────────────────────────────

def _update_call_count(db: Session, name: str):
    """
    更新模型调用次数与最后调用时间
    """
    try:
        record = db.query(ModelRecord).filter(
            ModelRecord.name == name,
            ModelRecord.is_active == True
        ).first()

        if record:
            record.call_count += 1
            record.last_called_at = datetime.utcnow()
            db.commit()
    except Exception as e:
        db.rollback()
        import logging
        logging.getLogger("execute_routes").error(
            f"更新调用统计失败: {e}"
        )
