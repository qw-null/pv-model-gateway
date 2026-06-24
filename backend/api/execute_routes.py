# backend/api/execute_routes.py

import time
import json
import math
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import ModelRecord, ExecutionLog
from db.panel import PVPanel  # 新增导入
from db.inverter import Inverter

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


# backend/api/execute_routes.py
# 在文件顶部已有 from db.panel import PVPanel

@router.post("/pv_diode", summary="光伏组件二极管模型")
async def run_pv_diode(body: dict, db: Session = Depends(get_db)):
    """
    支持两种调用方式：
    方式一：传入 panel_id + g_poa + t_cell，后端自动从组件库补全电学参数
    方式二：传入完整参数（isc/voc/imp/vmp/temp_coeff/g_ref/t_ref/g_poa/t_cell）
    panel_id 在两种方式下均可选，用于日志追踪。
    """
    # ── 方式一：panel_id 自动补全 ──────────────────────────────
    panel_id = body.get("panel_id")
    if panel_id:
        panel = db.query(PVPanel).filter(PVPanel.id == int(panel_id)).first()
        if not panel:
            raise HTTPException(status_code=404, detail=f"组件 ID={panel_id} 不存在")
        # 将组件字段注入 body（前端未传的才补全，已传的保留）
        panel_fields = {
            "isc": panel.isc, "voc": panel.voc,
            "imp": panel.imp, "vmp": panel.vmp,
            "temp_coeff": panel.temp_coeff,
            "g_ref": panel.g_ref, "t_ref": panel.t_ref,
        }
        for k, v in panel_fields.items():
            if k not in body and v is not None:
                body[k] = v

    # ── 参数完整性校验 ─────────────────────────────────────────
    required = ["isc", "voc", "imp", "vmp", "temp_coeff", "g_ref", "t_ref", "g_poa", "t_cell"]
    missing = [f for f in required if f not in body]
    if missing:
        raise HTTPException(status_code=422, detail={"message": "缺少必填参数", "errors": missing})

    entry = registry.get("pv_diode")
    if not entry:
        raise HTTPException(status_code=404, detail="模型 pv_diode 未注册")

    try:
        outputs, elapsed_ms = await safe_execute(entry["model_path"], body, timeout=30)
    except (TimeoutError, RuntimeError) as e:
        _log_execution(db, "pv_diode", body, None, False, str(e), 0)
        raise HTTPException(status_code=500, detail=str(e))

    safe_outputs = _sanitize_for_json(outputs)
    _log_execution(db, "pv_diode", body, safe_outputs, True, None, elapsed_ms)
    _update_call_count(db, "pv_diode")

    return {
        "success": True,
        "model": "pv_diode",
        "panel_id": panel_id,
        "outputs": safe_outputs,
        "execution_time_ms": elapsed_ms,
    }




@router.post("/inverter_from_ond", summary="逆变器模型（OND 数据库驱动）")
async def run_inverter_from_ond(body: dict, db: Session = Depends(get_db)):
    """
    支持两种调用方式：
    方式一：传入 inverter_id + p_dc，后端自动从逆变器数据库补全 Sandia 参数
    方式二：传入完整参数（p_aco / p_dco / p_so / c_o / p_dc）
    inverter_id 在两种方式下均可选，用于日志追踪。
    """
    # ── 方式一：inverter_id 自动补全 Sandia 参数 ──────────────
    inverter_id = body.get("inverter_id")
    if inverter_id:
        inv = db.query(Inverter).filter(
            Inverter.id == int(inverter_id)
        ).first()
        if not inv:
            raise HTTPException(
                status_code=404,
                detail=f"逆变器 ID={inverter_id} 不存在"
            )
        # 仅补全缺失字段，已传入的保留
        inverter_fields = {
            "p_aco": inv.p_aco,
            "p_dco": inv.p_dco,
            "p_so":  inv.p_so,
            "c_o":   inv.c_o,
        }
        for k, v in inverter_fields.items():
            if k not in body and v is not None and v != 0.0:
                body[k] = v

    # ── 参数完整性校验 ────────────────────────────────────────
    required = ["p_aco", "p_dco", "p_so", "c_o", "p_dc"]
    missing  = [f for f in required if f not in body]
    if missing:
        raise HTTPException(
            status_code=422,
            detail={"message": "缺少必填参数", "errors": missing}
        )

    entry = registry.get("inverter_from_ond")
    if not entry:
        raise HTTPException(
            status_code=404,
            detail="模型 inverter_from_ond 未注册"
        )

    try:
        outputs, elapsed_ms = await safe_execute(
            entry["model_path"], body, timeout=10
        )
    except (TimeoutError, RuntimeError) as e:
        _log_execution(db, "inverter_from_ond", body, None, False, str(e), 0)
        raise HTTPException(status_code=500, detail=str(e))

    safe_outputs = _sanitize_for_json(outputs)
    _log_execution(db, "inverter_from_ond", body, safe_outputs, True, None, elapsed_ms)
    _update_call_count(db, "inverter_from_ond")

    return {
        "success":          True,
        "model":            "inverter_from_ond",
        "inverter_id":      inverter_id,
        "outputs":          safe_outputs,
        "execution_time_ms": elapsed_ms,
    }


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
