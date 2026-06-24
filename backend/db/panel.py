# backend/db/panel.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, Text
from sqlalchemy.sql import func
from .database import Base

class PVPanel(Base):
    __tablename__ = "pv_panels"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    filename    = Column(String(255), nullable=False, comment="原始.pan文件名")
    file_path   = Column(String(500), nullable=False, comment="服务器存储路径")

    # ── 基本信息 ──────────────────────────────────────────────
    manufacturer    = Column(String(100), default="",    comment="厂家")
    model_name      = Column(String(100), default="",    comment="型号")
    is_bifacial     = Column(Boolean,     default=False, comment="是否双面")
    bifacial_factor = Column(Float,       default=0.0,   comment="双面率 %")

    # ── 制造商规格 ─────────────────────────────────────────────
    isc = Column(Float, default=0.0, comment="短路电流 A")
    voc = Column(Float, default=0.0, comment="开路电压 V")
    imp = Column(Float, default=0.0, comment="最大功率点电流 A")
    vmp = Column(Float, default=0.0, comment="最大功率点电压 V")

    # ── 三项温度系数 ───────────────────────────────────────────
    temp_coeff  = Column(Float, default=0.0,   comment="短路电流温度系数 muISC (mA/℃)")
    mu_voc_spec = Column(Float, default=-92.5, comment="开路电压温度系数 muVocSpec (mV/℃)")
    mu_pmp      = Column(Float, default=0.0,   comment="功率温度系数 muPmpReq (%/℃)")  # ★ 新增

    # ── 单二极管模型计算结果 ───────────────────────────────────
    g_ref      = Column(Float, default=1000.0, comment="运行条件 GRef W/m²")
    t_ref      = Column(Float, default=25.0,   comment="运行条件 TRef ℃")
    isc_calc   = Column(Float, default=0.0,    comment="计算短路电流 A")
    voc_calc   = Column(Float, default=0.0,    comment="计算开路电压 V")
    imp_calc   = Column(Float, default=0.0,    comment="计算最大功率点电流 A")
    vmp_calc   = Column(Float, default=0.0,    comment="计算最大功率点电压 V")
    pmp_calc   = Column(Float, default=0.0,    comment="计算最大功率 W")
    efficiency = Column(Float, default=0.0,    comment="组件效率 %")

    # ── 尺寸 ──────────────────────────────────────────────────
    length    = Column(Float, default=0.0, comment="长度 mm")
    width     = Column(Float, default=0.0, comment="宽度 mm")
    thickness = Column(Float, default=0.0, comment="厚度 mm")
    weight    = Column(Float, default=0.0, comment="重量 kg")
    area      = Column(Float, default=0.0, comment="组件面积 m²")

    # ── 电学曲线参数 ───────────────────────────────────────────
    r_series = Column(Float, default=0.037,  comment="串联电阻 Ω")
    r_shunt  = Column(Float, default=1000.0, comment="并联电阻 Ω")
    gamma    = Column(Float, default=1.255,  comment="二极管理想因子")

    # ── IAM 数据 ───────────────────────────────────────────────
    iam_angles = Column(JSON, default=list, comment="入射角数组")
    iam_values = Column(JSON, default=list, comment="IAM值数组")

    # ── 原始文件内容 ───────────────────────────────────────────
    raw_content = Column(Text, nullable=True, comment="pan文件原始内容")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
