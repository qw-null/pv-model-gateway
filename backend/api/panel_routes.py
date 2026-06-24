# backend/api/panel_routes.py
import os
from pathlib import Path
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from config import settings
from db.database import get_db
from db.panel import PVPanel
from core.pan_parser import parse_pan
from core.iv_curve import calc_curves_by_irradiance, calc_curves_by_temperature

router = APIRouter(prefix="/api/panels", tags=["组件管理"])

PANELS_DIR = Path(getattr(settings, "PANELS_DIR", "panels_repo"))
PANELS_DIR.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────────────────────
# Pydantic 请求体
# ─────────────────────────────────────────────────────────────

class PanelUpdateRequest(BaseModel):
    manufacturer:    Optional[str]   = Field(None, description="厂家名称")
    model_name:      Optional[str]   = Field(None, description="型号")
    is_bifacial:     Optional[bool]  = Field(None, description="是否双面组件")
    bifacial_factor: Optional[float] = Field(None, description="双面率 %")
    isc:             Optional[float] = Field(None, description="短路电流 A")
    voc:             Optional[float] = Field(None, description="开路电压 V")
    imp:             Optional[float] = Field(None, description="最大功率点电流 A")
    vmp:             Optional[float] = Field(None, description="最大功率点电压 V")
    temp_coeff:      Optional[float] = Field(None, description="短路电流温度系数 muISC (mA/℃)")
    mu_voc_spec:     Optional[float] = Field(None, description="开路电压温度系数 muVocSpec (mV/℃)")
    mu_pmp:          Optional[float] = Field(None, description="功率温度系数 muPmpReq (%/℃)")
    g_ref:           Optional[float] = Field(None, description="参考辐照度 W/m²")
    t_ref:           Optional[float] = Field(None, description="参考温度 ℃")
    isc_calc:        Optional[float] = Field(None, description="计算短路电流 A")
    voc_calc:        Optional[float] = Field(None, description="计算开路电压 V")
    imp_calc:        Optional[float] = Field(None, description="计算最大功率点电流 A")
    vmp_calc:        Optional[float] = Field(None, description="计算最大功率点电压 V")
    pmp_calc:        Optional[float] = Field(None, description="计算最大功率 W")
    efficiency:      Optional[float] = Field(None, description="组件效率 %")
    length:          Optional[float] = Field(None, description="长度 mm")
    width:           Optional[float] = Field(None, description="宽度 mm")
    thickness:       Optional[float] = Field(None, description="厚度 mm")
    weight:          Optional[float] = Field(None, description="重量 kg")
    area:            Optional[float] = Field(None, description="组件面积 m²")
    iam_angles:      Optional[list]  = Field(None, description="入射角数组")
    iam_values:      Optional[list]  = Field(None, description="IAM值数组")

class CurveRequest(BaseModel):
    mode: str = Field(
        "irradiance",
        description="计算模式：irradiance（不同辐照度）或 temperature（不同温度）"
    )
    irradiances:     list  = Field([1000, 800, 600, 400, 200], description="辐照度列表 W/m²（mode=irradiance 时生效）")
    temperatures:    list  = Field([0, 10, 25, 35, 45],        description="温度列表 ℃（mode=temperature 时生效）")
    base_temp:       float = Field(45.0,   description="基准温度 ℃（mode=irradiance 时使用）")
    base_irradiance: float = Field(1000.0, description="基准辐照度 W/m²（mode=temperature 时使用）")

# ─────────────────────────────────────────────────────────────
# Pydantic 响应模型（用于 Swagger 文档展示）
# ─────────────────────────────────────────────────────────────

class PanelSchema(BaseModel):
    """光伏组件完整信息"""
    id:              int   = Field(..., description="组件 ID")
    filename:        str   = Field(..., description="原始 .pan 文件名")
    manufacturer:    str   = Field(..., description="厂家")
    model_name:      str   = Field(..., description="型号")
    is_bifacial:     bool  = Field(..., description="是否双面组件")
    bifacial_factor: float = Field(..., description="双面率 %")

    # 电气参数
    isc:  float = Field(..., description="短路电流 Isc (A)")
    voc:  float = Field(..., description="开路电压 Voc (V)")
    imp:  float = Field(..., description="最大功率点电流 Imp (A)")
    vmp:  float = Field(..., description="最大功率点电压 Vmp (V)")

    # 三项温度系数
    temp_coeff:  float = Field(..., description="短路电流温度系数 muISC (mA/℃)")
    mu_voc_spec: float = Field(..., description="开路电压温度系数 muVocSpec (mV/℃)")
    mu_pmp:      float = Field(..., description="功率温度系数 muPmpReq (%/℃)")

    # 计算结果
    g_ref:      float = Field(..., description="参考辐照度 W/m²")
    t_ref:      float = Field(..., description="参考温度 ℃")
    isc_calc:   float = Field(..., description="计算短路电流 A")
    voc_calc:   float = Field(..., description="计算开路电压 V")
    imp_calc:   float = Field(..., description="计算最大功率点电流 A")
    vmp_calc:   float = Field(..., description="计算最大功率点电压 V")
    pmp_calc:   float = Field(..., description="计算最大功率 W")
    efficiency: float = Field(..., description="组件效率 %")

    # 尺寸
    length:    float = Field(..., description="长度 mm")
    width:     float = Field(..., description="宽度 mm")
    thickness: float = Field(..., description="厚度 mm")
    weight:    float = Field(..., description="重量 kg")
    area:      float = Field(..., description="组件面积 m²")

    # IAM
    iam_angles: list = Field(..., description="IAM 入射角数组")
    iam_values: list = Field(..., description="IAM 值数组")

    created_at: Optional[str] = Field(None, description="创建时间")
    updated_at: Optional[str] = Field(None, description="更新时间")

    class Config:
        from_attributes = True

class PanelDetailSchema(PanelSchema):
    """组件详情（含原始 .pan 文件内容）"""
    raw_content: Optional[str] = Field(None, description="原始 .pan 文件文本内容")

class PanelListResponse(BaseModel):
    """组件列表响应"""
    success:   bool              = Field(..., description="是否成功")
    data:      List[PanelSchema] = Field(..., description="组件数据列表")
    total:     int               = Field(..., description="总记录数")
    page:      int               = Field(..., description="当前页码")
    page_size: int               = Field(..., description="每页条数")

class PanelDetailResponse(BaseModel):
    """组件详情响应"""
    success: bool              = Field(..., description="是否成功")
    data:    PanelDetailSchema = Field(..., description="组件详情")

class ManufacturersResponse(BaseModel):
    """厂家列表响应"""
    success: bool       = Field(..., description="是否成功")
    data:    List[str]  = Field(..., description="厂家名称列表")

class CurveSeries(BaseModel):
    label:    str         = Field(...,  description="曲线标签，如 '1000 W/m²'")
    voltages: List[float] = Field(...,  description="电压点列表 V")
    currents: List[float] = Field(...,  description="电流点列表 A")
    powers:   List[float] = Field(...,  description="功率点列表 W")
    # iv_curve.py 还会返回 voc/isc/vmp/imp/pmp/irradiance/temperature，
    # 允许额外字段通过，不触发校验失败
    model_config = {"extra": "allow"}


class CurvesResponse(BaseModel):
    """IV/PV 曲线响应"""
    success: bool             = Field(..., description="是否成功")
    mode:    str              = Field(..., description="计算模式：irradiance 或 temperature")
    data:    List[CurveSeries]= Field(..., description="各条件下的曲线数据")

# ─────────────────────────────────────────────────────────────
# 内部工具函数
# ─────────────────────────────────────────────────────────────

def _panel_to_dict(p: PVPanel, include_raw: bool = False) -> dict:
    """将 ORM 对象转换为字典，用于接口响应。"""
    result = {
        "id":              p.id,
        "filename":        p.filename,
        "manufacturer":    p.manufacturer,
        "model_name":      p.model_name,
        "is_bifacial":     p.is_bifacial,
        "bifacial_factor": p.bifacial_factor,

        # 电气参数
        "isc":  p.isc,
        "voc":  p.voc,
        "imp":  p.imp,
        "vmp":  p.vmp,

        # ── 三项温度系数（核心修改）────────────────────────────
        "temp_coeff":  p.temp_coeff,               # 短路电流温度系数 muISC (mA/℃)
        "mu_voc_spec": p.mu_voc_spec,              # 开路电压温度系数 muVocSpec (mV/℃) ★补充
        "mu_pmp":      p.mu_pmp if hasattr(p, "mu_pmp") else 0.0,  # 功率温度系数 muPmpReq (%/℃) ★新增

        # 计算结果
        "g_ref":      p.g_ref,
        "t_ref":      p.t_ref,
        "isc_calc":   p.isc_calc,
        "voc_calc":   p.voc_calc,
        "imp_calc":   p.imp_calc,
        "vmp_calc":   p.vmp_calc,
        "pmp_calc":   p.pmp_calc,
        "efficiency": p.efficiency,

        # 尺寸
        "length":    p.length,
        "width":     p.width,
        "thickness": p.thickness,
        "weight":    p.weight,
        "area":      p.area,

        # IAM
        "iam_angles": p.iam_angles or [],
        "iam_values": p.iam_values or [],

        "created_at": str(p.created_at) if p.created_at else None,
        "updated_at": str(p.updated_at) if p.updated_at else None,
    }
    if include_raw:
        result["raw_content"] = p.raw_content
    return result

# ─────────────────────────────────────────────────────────────
# 接口：上传 .pan 文件
# ─────────────────────────────────────────────────────────────

@router.post(
    "/upload",
    summary="上传 .pan 文件",
    description="上传 PVsyst `.pan` 格式的光伏组件文件，系统自动解析并入库。重复文件名不会覆盖已有记录。",
    response_model=PanelDetailResponse,
    responses={400: {"description": "文件格式错误，仅支持 .pan"}},
)
async def upload_panel(
    file: UploadFile = File(..., description="PVsyst .pan 格式组件文件"),
    db:   Session    = Depends(get_db),
):
    if not file.filename.lower().endswith(".pan"):
        raise HTTPException(status_code=400, detail="仅支持 .pan 格式文件")

    content_bytes = await file.read()
    try:
        content = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        content = content_bytes.decode("latin-1")

    save_path = PANELS_DIR / file.filename
    with open(save_path, "wb") as f:
        f.write(content_bytes)

    parsed = parse_pan(content)
    panel = PVPanel(
        filename=file.filename,
        file_path=str(save_path.resolve()),
        raw_content=content,
        **parsed,
    )
    db.add(panel)
    db.commit()
    db.refresh(panel)
    return {"success": True, "data": _panel_to_dict(panel, include_raw=True)}

# ─────────────────────────────────────────────────────────────
# 接口：获取组件列表
# ─────────────────────────────────────────────────────────────

@router.get(
    "",
    summary="获取组件列表",
    description=(
        "分页查询光伏组件列表，支持按**厂家**精确筛选和按**型号**模糊搜索。\n\n"
        "返回字段包含组件基本信息、电气参数（含三项温度系数）及尺寸信息。"
    ),
    response_model=PanelListResponse,
)
def list_panels(
    manufacturer: Optional[str] = None,
    model_name:   Optional[str] = None,
    page:         int = 1,
    page_size:    int = 100,
    db:           Session = Depends(get_db),
):
    query = db.query(PVPanel)
    if manufacturer:
        query = query.filter(PVPanel.manufacturer == manufacturer)
    if model_name:
        query = query.filter(PVPanel.model_name.like(f"%{model_name}%"))

    total  = query.count()
    panels = (
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

# ─────────────────────────────────────────────────────────────
# 接口：获取厂家列表
# ─────────────────────────────────────────────────────────────

@router.get(
    "/manufacturers",
    summary="获取厂家列表",
    description="返回数据库中所有已入库组件的**厂家名称去重列表**，按字母顺序排列，常用于前端下拉筛选框。",
    response_model=ManufacturersResponse,
)
def get_manufacturers(db: Session = Depends(get_db)):
    rows = (
        db.query(PVPanel.manufacturer)
        .distinct()
        .order_by(PVPanel.manufacturer)
        .all()
    )
    return {"success": True, "data": [r[0] for r in rows if r[0]]}

# ─────────────────────────────────────────────────────────────
# 接口：获取组件详情
# ─────────────────────────────────────────────────────────────

@router.get(
    "/{panel_id}",
    summary="获取组件详情",
    description=(
        "根据组件 ID 获取完整的组件信息，在基础字段之外额外返回：\n\n"
        "- `temp_coeff`：**短路电流温度系数** muISC (mA/℃)\n"
        "- `mu_voc_spec`：**开路电压温度系数** muVocSpec (mV/℃)\n"
        "- `mu_pmp`：**功率温度系数** muPmpReq (%/℃)\n"
        "- `raw_content`：原始 `.pan` 文件文本内容"
    ),
    response_model=PanelDetailResponse,
    responses={404: {"description": "组件不存在"}},
)
def get_panel(panel_id: int, db: Session = Depends(get_db)):
    panel = db.query(PVPanel).filter(PVPanel.id == panel_id).first()
    if not panel:
        raise HTTPException(status_code=404, detail="组件不存在")
    return {"success": True, "data": _panel_to_dict(panel, include_raw=True)}

# ─────────────────────────────────────────────────────────────
# 接口：修改组件信息
# ─────────────────────────────────────────────────────────────

@router.put(
    "/{panel_id}",
    summary="修改组件信息",
    description="局部更新组件字段，仅传入需要修改的字段即可（支持 `mu_voc_spec`、`mu_pmp` 等温度系数字段）。修改 `length`/`width`/`pmp_calc` 时自动重算面积与效率。",
    response_model=PanelDetailResponse,
    responses={404: {"description": "组件不存在"}},
)
def update_panel(
    panel_id: int,
    body:     PanelUpdateRequest,
    db:       Session = Depends(get_db),
):
    panel = db.query(PVPanel).filter(PVPanel.id == panel_id).first()
    if not panel:
        raise HTTPException(status_code=404, detail="组件不存在")

    for field, value in body.model_dump(exclude_none=True).items():
        setattr(panel, field, value)

    if panel.length and panel.width:
        panel.area = round(panel.length * panel.width / 1e6, 6)
    if panel.pmp_calc and panel.g_ref and panel.area:
        panel.efficiency = round(panel.pmp_calc / (panel.g_ref * panel.area) * 100, 4)

    db.commit()
    db.refresh(panel)
    return {"success": True, "data": _panel_to_dict(panel)}

# ─────────────────────────────────────────────────────────────
# 接口：删除组件
# ─────────────────────────────────────────────────────────────

@router.delete(
    "/{panel_id}",
    summary="删除组件",
    description="删除指定组件记录，同时删除服务器上的 `.pan` 原始文件。",
    responses={404: {"description": "组件不存在"}},
)
def delete_panel(panel_id: int, db: Session = Depends(get_db)):
    panel = db.query(PVPanel).filter(PVPanel.id == panel_id).first()
    if not panel:
        raise HTTPException(status_code=404, detail="组件不存在")

    try:
        if panel.file_path and os.path.exists(panel.file_path):
            os.remove(panel.file_path)
    except Exception:
        pass

    db.delete(panel)
    db.commit()
    return {"success": True, "message": "删除成功"}

# ─────────────────────────────────────────────────────────────
# 接口：计算 IV/PV 电学曲线
# ─────────────────────────────────────────────────────────────
@router.post(
    "/{panel_id}/curves",
    summary="计算 IV/PV 电学曲线（getCurves）",
    description=(
        "基于单二极管模型计算组件在不同工况下的 IV 及 PV 曲线。\n\n"
        "**mode = `irradiance`​**（默认）：固定温度，计算多个辐照度下的曲线。\n\n"
        "**mode = `temperature`​**：固定辐照度，计算多个温度下的曲线，"
        "计算中使用 `temp_coeff`（muISC）与 `mu_voc_spec`（muVocSpec）两项温度系数。\n\n"
        "每条曲线返回 `voltages`、`currents`、`powers` 三组数据点，可直接用于前端图表渲染。"
    ),
    response_model=CurvesResponse,
    responses={404: {"description": "组件不存在"}},
)
def get_curves(
    panel_id: int,
    body:     CurveRequest,
    db:       Session = Depends(get_db),
):
    panel = db.query(PVPanel).filter(PVPanel.id == panel_id).first()
    if not panel:
        raise HTTPException(status_code=404, detail="组件不存在")

    panel_params = {
        "isc":         panel.isc,
        "voc":         panel.voc,
        "imp":         panel.imp,
        "vmp":         panel.vmp,
        "r_series":    panel.r_series    or 0.037,
        "r_shunt":     panel.r_shunt     or 1000.0,
        "gamma":       panel.gamma       or 1.255,
        "temp_coeff":  panel.temp_coeff  or 6.22,
        "mu_voc_spec": panel.mu_voc_spec or -92.5,
        "g_ref":       panel.g_ref       or 1000.0,
        "t_ref":       panel.t_ref       or 25.0,
    }

    if body.mode == "temperature":
        curves = calc_curves_by_temperature(
            panel_params, body.temperatures, body.base_irradiance
        )
        # ★ 注入 label：iv_curve.py 不生成此字段，但 CurveSeries 要求必填
        for curve in curves:
            curve["label"] = f"{curve['temperature']} ℃"
    else:
        curves = calc_curves_by_irradiance(
            panel_params, body.irradiances, body.base_temp
        )
        # ★ 注入 label
        for curve in curves:
            curve["label"] = f"{curve['irradiance']} W/m²"

    return {"success": True, "data": curves, "mode": body.mode}


