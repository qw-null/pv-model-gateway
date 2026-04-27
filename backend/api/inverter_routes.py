# backend/api/inverter_routes.py
import os
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session

from config import settings
from db.database import get_db
from db.inverter import Inverter
from core.ond_parser import parse_ond

router = APIRouter(prefix="/api/inverters", tags=["逆变器管理"])

INVERTERS_DIR = Path(getattr(settings, "INVERTERS_DIR", "inverters_repo"))
INVERTERS_DIR.mkdir(parents=True, exist_ok=True)


# ── Pydantic Schema ────────────────────────────────────────────
class InverterUpdateRequest(BaseModel):
    manufacturer:        Optional[str]   = None
    model_name:          Optional[str]   = None
    vmp_min:             Optional[float] = None
    vmp_nom:             Optional[float] = None
    vmp_max:             Optional[float] = None
    vdc_max:             Optional[float] = None
    vac_out:             Optional[float] = None
    pac_nom:             Optional[float] = None
    pac_max:             Optional[float] = None
    efficiency:          Optional[float] = None
    temp_pac_nom:        Optional[float] = None
    temp_pac_max:        Optional[float] = None
    temp_derating:       Optional[float] = None
    pac_derating:        Optional[float] = None
    temp_derating_limit: Optional[float] = None
    efficiency_curves:   Optional[dict]  = None


def _to_dict(inv: Inverter, include_raw: bool = False) -> dict:
    result = {
        "id":                  inv.id,
        "filename":            inv.filename,
        "manufacturer":        inv.manufacturer,
        "model_name":          inv.model_name,
        "vmp_min":             inv.vmp_min,
        "vmp_nom":             inv.vmp_nom,
        "vmp_max":             inv.vmp_max,
        "vdc_max":             inv.vdc_max,
        "vac_out":             inv.vac_out,
        "pac_nom":             inv.pac_nom,
        "pac_max":             inv.pac_max,
        "iac_nom":             inv.iac_nom,
        "iac_max":             inv.iac_max,
        "efficiency":          inv.efficiency,
        "efficiency_curves":   inv.efficiency_curves or {},
        "temp_pac_nom":        inv.temp_pac_nom,
        "temp_pac_max":        inv.temp_pac_max,
        "temp_derating":       inv.temp_derating,
        "pac_derating":        inv.pac_derating,
        "temp_derating_limit": inv.temp_derating_limit,
        "created_at":          str(inv.created_at) if inv.created_at else None,
        "updated_at":          str(inv.updated_at) if inv.updated_at else None,
    }
    if include_raw:
        result["raw_content"] = inv.raw_content
    return result


# ── 上传 .OND 文件 ─────────────────────────────────────────────
@router.post("/upload", summary="上传 .OND 文件")
async def upload_inverter(
    file: UploadFile = File(...),
    db:   Session    = Depends(get_db)
):
    if not file.filename.lower().endswith(".ond"):
        raise HTTPException(status_code=400, detail="仅支持 .OND / .ond 格式文件")

    content_bytes = await file.read()
    try:
        content = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        content = content_bytes.decode("latin-1")

    save_path = INVERTERS_DIR / file.filename
    with open(save_path, "wb") as f:
        f.write(content_bytes)

    parsed = parse_ond(content)

    inv = Inverter(
        filename    = file.filename,
        file_path   = str(save_path.resolve()),
        raw_content = content,
        **parsed,
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)

    return {"success": True, "data": _to_dict(inv)}


# ── 列表（搜索 + 分页）────────────────────────────────────────
@router.get("", summary="获取逆变器列表")
def list_inverters(
    manufacturer: Optional[str] = None,
    model_name:   Optional[str] = None,
    page:         int = 1,
    page_size:    int = 10,
    db:           Session = Depends(get_db)
):
    query = db.query(Inverter)
    if manufacturer:
        query = query.filter(Inverter.manufacturer == manufacturer)
    if model_name:
        query = query.filter(Inverter.model_name.like(f"%{model_name}%"))

    total    = query.count()
    inverters = (
        query
        .order_by(Inverter.manufacturer, Inverter.model_name)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "success":   True,
        "data":      [_to_dict(i) for i in inverters],
        "total":     total,
        "page":      page,
        "page_size": page_size,
    }


# ── 厂家列表 ───────────────────────────────────────────────────
@router.get("/manufacturers", summary="获取厂家列表")
def get_manufacturers(db: Session = Depends(get_db)):
    rows = db.query(Inverter.manufacturer).distinct().order_by(Inverter.manufacturer).all()
    return {"success": True, "data": [r[0] for r in rows if r[0]]}


# ── 详情 ──────────────────────────────────────────────────────
@router.get("/{inv_id}", summary="获取逆变器详情")
def get_inverter(inv_id: int, db: Session = Depends(get_db)):
    inv = db.query(Inverter).filter(Inverter.id == inv_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="逆变器不存在")
    return {"success": True, "data": _to_dict(inv, include_raw=True)}


# ── 修改 ──────────────────────────────────────────────────────
@router.put("/{inv_id}", summary="修改逆变器信息")
def update_inverter(
    inv_id: int,
    body:   InverterUpdateRequest,
    db:     Session = Depends(get_db)
):
    inv = db.query(Inverter).filter(Inverter.id == inv_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="逆变器不存在")

    for field, value in body.model_dump(exclude_none=True).items():
        setattr(inv, field, value)

    # 自动重算电流
    if inv.vac_out and inv.vac_out > 0:
        inv.iac_nom = round(inv.pac_nom * 1000 / inv.vac_out, 2)
        inv.iac_max = round(inv.pac_max * 1000 / inv.vac_out, 2)

    db.commit()
    db.refresh(inv)
    return {"success": True, "data": _to_dict(inv)}


# ── 删除 ──────────────────────────────────────────────────────
@router.delete("/{inv_id}", summary="删除逆变器")
def delete_inverter(inv_id: int, db: Session = Depends(get_db)):
    inv = db.query(Inverter).filter(Inverter.id == inv_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="逆变器不存在")
    try:
        if inv.file_path and os.path.exists(inv.file_path):
            os.remove(inv.file_path)
    except Exception:
        pass
    db.delete(inv)
    db.commit()
    return {"success": True, "message": "删除成功"}
