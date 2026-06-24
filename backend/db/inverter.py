# backend/db/inverter.py
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text
from sqlalchemy.sql import func
from .database import Base

class Inverter(Base):
    __tablename__ = "inverters"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    filename   = Column(String(255), nullable=False, comment="原始文件名")
    file_path  = Column(String(500), nullable=False, comment="服务器存储路径")

    # ── 基本信息 ──────────────────────────────────────────────
    manufacturer = Column(String(100), default="", comment="厂家")
    model_name   = Column(String(100), default="", comment="型号")

    # ── 输入侧 ────────────────────────────────────────────────
    vmp_min  = Column(Float, default=0.0, comment="最小MPP电压 V")
    vmp_nom  = Column(Float, default=0.0, comment="标称MPP电压 V")
    vmp_max  = Column(Float, default=0.0, comment="最大MPP电压 V")
    vdc_max  = Column(Float, default=0.0, comment="绝对最大直流电压 V")

    # ── 输出侧 ────────────────────────────────────────────────
    vac_out  = Column(Float, default=0.0, comment="输出电压 V")
    pac_nom  = Column(Float, default=0.0, comment="标称交流功率 kW")
    pac_max  = Column(Float, default=0.0, comment="最大交流功率 kW")
    iac_nom  = Column(Float, default=0.0, comment="标称输出电流 A（只读）")
    iac_max  = Column(Float, default=0.0, comment="最大输出电流 A（只读）")
    efficiency = Column(Float, default=0.0, comment="额定效率 %")

    # ── 效率曲线数据（JSON）────────────────────────────────────
    efficiency_curves = Column(JSON, default=dict, comment="效率曲线数据")

    # ── 温度限制 ───────────────────────────────────────────────
    temp_pac_nom       = Column(Float, default=45.0, comment="标称功率温度上限 ℃")
    temp_pac_max       = Column(Float, default=35.0, comment="最大功率温度点 ℃")
    temp_derating      = Column(Float, default=60.0, comment="高温功率限制触发温度 ℃")
    pac_derating       = Column(Float, default=0.0,  comment="高温功率限制值 kW")
    temp_derating_limit= Column(Float, default=62.0, comment="高温功率限制极限温度 ℃")

    # ── Sandia 模型拟合参数（由 ond_parser 解析时计算写入）──────
    p_aco = Column(Float, default=0.0, comment="Sandia Paco: 额定交流功率 W")
    p_dco = Column(Float, default=0.0, comment="Sandia Pdco: 额定直流功率 W（效率曲线拟合）")
    p_so  = Column(Float, default=0.0, comment="Sandia Pso:  启动自耗功率 W（效率曲线拟合）")
    c_o   = Column(Float, default=0.0, comment="Sandia Co:   二次修正系数 1/W（效率曲线拟合）")

    # ── 原始文件 ───────────────────────────────────────────────
    raw_content = Column(Text, nullable=True, comment="OND文件原始内容")
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), onupdate=func.now())
