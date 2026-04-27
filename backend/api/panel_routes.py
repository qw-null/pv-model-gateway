# backend/api/panel_routes.py
import os
import shutil
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session

from config import settings
from db.database import get_db
from db.panel import PVPanel
from core.pan_parser import parse_pan
from core.iv_curve import calc_curves_by_irradiance, calc_curves_by_temperature
from pydantic import BaseModel as PydanticBase

router = APIRouter(prefix="/api/panels", tags=["组件管理"])

# 固定存储目录
PANELS_DIR = Path(getattr(settings, "PANELS_DIR", "panels_repo"))
PANELS_DIR.mkdir(parents=True, exist_ok=True)


# ── Pydantic Schema ────────────────────────────────────────────
class PanelUpdateRequest(BaseModel):
    manufacturer:    Optional[str]   = None
    model_name:      Optional[str]   = None
    is_bifacial:     Optional[bool]  = None
    bifacial_factor: Optional[float] = None
    isc:             Optional[float] = None
    voc:             Optional[float] = None
    imp:             Optional[float] = None
    vmp:             Optional[float] = None
    temp_coeff:      Optional[float] = None
    g_ref:           Optional[float] = None
    t_ref:           Optional[float] = None
    isc_calc:        Optional[float] = None
    voc_calc:        Optional[float] = None
    imp_calc:        Optional[float] = None
    vmp_calc:        Optional[float] = None
    pmp_calc:        Optional[float] = None
    efficiency:      Optional[float] = None
    length:          Optional[float] = None
    width:           Optional[float] = None
    thickness:       Optional[float] = None
    weight:          Optional[float] = None
    area:            Optional[float] = None
    iam_angles:      Optional[list]  = None
    iam_values:      Optional[list]  = None

# 新增请求体
class CurveRequest(PydanticBase):
    mode:            str   = "irradiance"          # "irradiance" | "temperature"
    irradiances:     list  = [1000, 800, 600, 400, 200]
    temperatures:    list  = [0, 10, 25, 35, 45]
    base_temp:       float = 45.0
    base_irradiance: float = 1000.0


def _panel_to_dict(p: PVPanel, include_raw: bool = False) -> dict:
    result = {
        "id":             p.id,
        "filename":       p.filename,
        "manufacturer":   p.manufacturer,
        "model_name":     p.model_name,
        "is_bifacial":    p.is_bifacial,
        "bifacial_factor":p.bifacial_factor,
        "isc":            p.isc,
        "voc":            p.voc,
        "imp":            p.imp,
        "vmp":            p.vmp,
        "temp_coeff":     p.temp_coeff,
        "g_ref":          p.g_ref,
        "t_ref":          p.t_ref,
        "isc_calc":       p.isc_calc,
        "voc_calc":       p.voc_calc,
        "imp_calc":       p.imp_calc,
        "vmp_calc":       p.vmp_calc,
        "pmp_calc":       p.pmp_calc,
        "efficiency":     p.efficiency,
        "length":         p.length,
        "width":          p.width,
        "thickness":      p.thickness,
        "weight":         p.weight,
        "area":           p.area,
        "iam_angles":     p.iam_angles or [],
        "iam_values":     p.iam_values or [],
        "created_at":     str(p.created_at) if p.created_at else None,
        "updated_at":     str(p.updated_at) if p.updated_at else None,
    }
    if include_raw:
        result["raw_content"] = p.raw_content
    return result


# ── 上传 .pan 文件 ─────────────────────────────────────────────
@router.post("/upload", summary="上传 .pan 文件")
async def upload_panel(
    file: UploadFile = File(...),
    db:   Session    = Depends(get_db)
):
    if not file.filename.lower.endswith(".pan"):
        raise HTTPException(status_code=400, detail="仅支持 .pan 格式文件")

    content_bytes = await file.read()
    try:
        content = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        content = content_bytes.decode("latin-1")

    # 保存文件到固定目录
    save_path = PANELS_DIR / file.filename
    with open(save_path, "wb") as f:
        f.write(content_bytes)

    # 解析 pan 文件
    parsed = parse_pan(content)

    # 写入数据库
    panel = PVPanel(
        filename=file.filename,
        file_path=str(save_path.resolve()),
        raw_content=content,
        **parsed,
    )
    db.add(panel)
    db.commit()
    db.refresh(panel)

    return {"success": True, "data": _panel_to_dict(panel)}


# ── 获取组件列表 ───────────────────────────────────────────────
# panel_routes.py — 替换 list_panels 接口

@router.get("", summary="获取组件列表")
def list_panels(
    manufacturer: Optional[str] = None,   # 厂家筛选
    model_name:   Optional[str] = None,   # 型号模糊搜索
    page:         int = 1,
    page_size:    int = 100,
    db:           Session = Depends(get_db)
):
    query = db.query(PVPanel)

    if manufacturer:
        query = query.filter(PVPanel.manufacturer == manufacturer)
    if model_name:
        query = query.filter(PVPanel.model_name.like(f"%{model_name}%"))

    total   = query.count()
    panels  = (
        query
        .order_by(PVPanel.manufacturer, PVPanel.model_name)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "success":   True,
        "data":      [_panel_to_dict(p) for p in panels],
        "total":     total,
        "page":      page,
        "page_size": page_size,
    }


# 新增：获取所有厂家列表（用于下拉筛选）
@router.get("/manufacturers", summary="获取厂家列表")
def get_manufacturers(db: Session = Depends(get_db)):
    rows = db.query(PVPanel.manufacturer).distinct().order_by(PVPanel.manufacturer).all()
    return {"success": True, "data": [r[0] for r in rows if r[0]]}



# ── 获取组件详情 ───────────────────────────────────────────────
@router.get("/{panel_id}", summary="获取组件详情")
def get_panel(panel_id: int, db: Session = Depends(get_db)):
    panel = db.query(PVPanel).filter(PVPanel.id == panel_id).first()
    if not panel:
        raise HTTPException(status_code=404, detail="组件不存在")
    return {"success": True, "data": _panel_to_dict(panel,include_raw=True)}


# ── 修改组件信息 ───────────────────────────────────────────────
@router.put("/{panel_id}", summary="修改组件信息")
def update_panel(
    panel_id: int,
    body:     PanelUpdateRequest,
    db:       Session = Depends(get_db)
):
    panel = db.query(PVPanel).filter(PVPanel.id == panel_id).first()
    if not panel:
        raise HTTPException(status_code=404, detail="组件不存在")

    for field, value in body.model_dump(exclude_none=True).items():
        setattr(panel, field, value)

    # 自动重算面积和效率
    if panel.length and panel.width:
        panel.area = round(panel.length * panel.width / 1e6, 6)
    if panel.pmp_calc and panel.g_ref and panel.area:
        panel.efficiency = round(panel.pmp_calc / (panel.g_ref * panel.area) * 100, 4)

    db.commit()
    db.refresh(panel)
    return {"success": True, "data": _panel_to_dict(panel)}


# ── 删除组件 ───────────────────────────────────────────────────
@router.delete("/{panel_id}", summary="删除组件")
def delete_panel(panel_id: int, db: Session = Depends(get_db)):
    panel = db.query(PVPanel).filter(PVPanel.id == panel_id).first()
    if not panel:
        raise HTTPException(status_code=404, detail="组件不存在")

    # 删除文件
    try:
        if panel.file_path and os.path.exists(panel.file_path):
            os.remove(panel.file_path)
    except Exception:
        pass

    db.delete(panel)
    db.commit()
    return {"success": True, "message": "删除成功"}

@router.post("/{panel_id}/curves", summary="计算电学曲线")
def get_curves(
    panel_id: int,
    body:     CurveRequest,
    db:       Session = Depends(get_db)
):
    panel = db.query(PVPanel).filter(PVPanel.id == panel_id).first()
    if not panel:
        raise HTTPException(status_code=404, detail="组件不存在")

    panel_params = {
        "isc":          panel.isc,
        "voc":          panel.voc,
        "imp":          panel.imp,
        "vmp":          panel.vmp,
        "r_series":     panel.r_series    or 0.037,
        "r_shunt":      panel.r_shunt     or 1000.0,
        "gamma":        panel.gamma       or 1.255,
        "temp_coeff":   panel.temp_coeff  or 6.22,
        "mu_voc_spec":  panel.mu_voc_spec or -92.5,
        "g_ref":        panel.g_ref       or 1000.0,
        "t_ref":        panel.t_ref       or 25.0,
    }

    if body.mode == "temperature":
        curves = calc_curves_by_temperature(
            panel_params, body.temperatures, body.base_irradiance
        )
    else:
        curves = calc_curves_by_irradiance(
            panel_params, body.irradiances, body.base_temp
        )

    return {"success": True, "data": curves, "mode": body.mode}
