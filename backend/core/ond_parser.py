# backend/core/ond_parser.py
"""
解析 PVsyst .OND 文件（Version 6.x / 7.x）
字段对照真实文件格式进行精确映射
"""
import re
import numpy as np


# ══════════════════════════════════════════════════════════════
# 基础工具函数
# ══════════════════════════════════════════════════════════════

def _get(content: str, key: str, default=None):
    """精确匹配行首 key=value，忽略大小写"""
    pattern = rf"(?mi)^\s*{re.escape(key)}\s*=\s*(.+)$"
    match = re.search(pattern, content)
    if match:
        return match.group(1).strip().strip('"').strip("'")
    return default


def _get_float(content: str, key: str, default: float = 0.0) -> float:
    val = _get(content, key)
    try:
        return float(val) if val is not None else default
    except (ValueError, TypeError):
        return default


def _get_str(content: str, key: str, default: str = "") -> str:
    val = _get(content, key, default)
    return str(val).strip() if val else default


def _parse_profile_block(block: str) -> tuple:
    """
    解析 TCubicProfile 块中的 Point_N=pdc_w,pac_w 数据点。
    真实格式：Point_1=75.0,0.0（单位均为 W）
    过滤 pdc=0 且 pac=0 的无效占位点。
    返回 (pdc_w_list, pac_w_list)
    """
    points = re.findall(r"Point_\d+=\s*([\d.]+)\s*,\s*([\d.]+)", block)
    pdc_list = []
    pac_list = []
    for pdc_str, pac_str in points:
        pdc = float(pdc_str)
        pac = float(pac_str)
        # 过滤无效占位点（pdc=0 且 pac=0）
        if pdc == 0.0 and pac == 0.0:
            continue
        pdc_list.append(pdc)
        pac_list.append(pac)
    return pdc_list, pac_list


def _parse_efficiency_curves(content: str) -> dict:
    """
    解析三个电压档位的效率曲线。
    VNomEff=430.0,556.0,850.0,  ← 三档电压
    ProfilPIOV1/V2/V3           ← 对应低/中/高压曲线
    Point 格式：Pdc(W), Pac(W)
    """
    curves = {}
    v_line   = _get(content, "VNomEff", "")
    voltages = [float(v.strip()) for v in v_line.split(",") if v.strip()]
    labels   = ["low", "mid", "high"]

    for idx, profile_key in enumerate(["ProfilPIOV1", "ProfilPIOV2", "ProfilPIOV3"]):
        block_match = re.search(
            rf"(?s){re.escape(profile_key)}=TCubicProfile(.+?)End of TCubicProfile",
            content
        )
        if not block_match:
            continue
        block = block_match.group(1)
        pdc_list, pac_list = _parse_profile_block(block)
        if not pdc_list:
            continue

        voltage = voltages[idx] if idx < len(voltages) else 0.0
        label   = labels[idx]

        # 计算效率列表（%）
        eta_list = [
            round(pac / pdc * 100, 6) if pdc > 0 else 0.0
            for pdc, pac in zip(pdc_list, pac_list)
        ]

        curves[label] = {
            "voltage":  voltage,
            "pdc_list": pdc_list,   # W
            "pac_list": pac_list,   # W
            "eta_list": eta_list,   # %
        }
    return curves


# ══════════════════════════════════════════════════════════════
# Sandia 参数拟合（基于真实 OND 数据结构）
# ══════════════════════════════════════════════════════════════

def _fit_sandia_params(content: str, pac_nom_kw: float,
                       efficiency_curves: dict) -> dict:
    """
    从 OND 文件直接读取 / 精确拟合 Sandia 模型四参数：

    p_aco — PNomConv × 1000（额定交流功率 W，直读）
    p_so  — PSeuil（启动阈值 W，直读，OND 文件直接给出）
    p_dco — PInEffMax（峰值效率对应的 Pdc W，直读）；
            若缺失则从中压曲线找 η 最高点对应的 Pdc
    c_o   — 对中压曲线 (Pdc-Pso, Pac) 做二次最小二乘拟合的二次项系数

    Point 数据单位：W（非百分比、非 kW）
    """
    p_aco = pac_nom_kw * 1000.0   # kW → W

    # ── p_so：直接读 PSeuil（启动阈值，W）──────────────────────
    p_so = _get_float(content, "PSeuil", 0.0)
    if p_so <= 0.0:
        p_so = p_aco * 0.005      # 兜底：0.5% Paco

    # ── p_dco：直接读 PInEffMax（峰值效率点 Pdc，W）────────────
    p_dco = _get_float(content, "PInEffMax", 0.0)

    # 若 PInEffMax 缺失，从中压曲线找效率最高点的 Pdc
    if p_dco <= 0.0:
        curve = (efficiency_curves.get("mid")
                 or efficiency_curves.get("low")
                 or efficiency_curves.get("high"))
        if curve and curve.get("pdc_list") and curve.get("eta_list"):
            pdc_arr = curve["pdc_list"]
            eta_arr = curve["eta_list"]
            best_idx = eta_arr.index(max(eta_arr))
            p_dco = pdc_arr[best_idx]

    if p_dco <= 0.0:
        p_dco = p_aco / 0.975     # 最终兜底：假设峰值效率 97.5%

    # ── c_o：最小二乘二次拟合（使用中压曲线）───────────────────
    # Sandia 式61：Pac = A*(Pdc-Pso) + Co*(Pdc-Pso)^2
    # 其中 A = Paco/(Pdco-Pso) - Co*(Pdco-Pso)
    # 直接对 delta=Pdc-Pso, Pac 做二次多项式拟合，coeffs[0]=Co
    c_o = 0.0
    curve = (efficiency_curves.get("mid")
             or efficiency_curves.get("low")
             or efficiency_curves.get("high"))

    if curve and curve.get("pdc_list") and curve.get("pac_list"):
        pdc_arr = np.array(curve["pdc_list"], dtype=float)
        pac_arr = np.array(curve["pac_list"], dtype=float)

        # 只取 Pdc > Pso 且 Pac > 0 的有效点
        mask    = (pdc_arr > p_so) & (pac_arr > 0)
        pdc_arr = pdc_arr[mask]
        pac_arr = pac_arr[mask]

        if len(pdc_arr) >= 3:
            delta = pdc_arr - p_so
            try:
                # 二次拟合：pac = Co*delta^2 + A*delta
                # coeffs[0]=Co，coeffs[1]=A，coeffs[2]=截距（理论上≈0）
                coeffs = np.polyfit(delta, pac_arr, 2)
                c_o    = float(coeffs[0])
            except Exception:
                c_o = 0.0

    return {
        "p_aco": round(p_aco,  4),
        "p_dco": round(p_dco,  4),
        "p_so":  round(p_so,   4),
        "c_o":   round(c_o,    8),
    }


# ══════════════════════════════════════════════════════════════
# 主解析函数
# ══════════════════════════════════════════════════════════════

def parse_ond(content: str) -> dict:
    """
    解析 .OND 文件，返回与 Inverter 数据库字段对应的字典
    """
    # ── 基本信息 ──────────────────────────────────────────────
    manufacturer = _get_str(content, "Manufacturer")
    model_name   = _get_str(content, "Model")

    # ── 输入侧 ────────────────────────────────────────────────
    vmp_min = _get_float(content, "VMppMin")
    vmp_max = _get_float(content, "VMPPMax")
    if vmp_max == 0.0:
        vmp_max = _get_float(content, "VMppMax")
    vmp_nom = _get_float(content, "VmppNom")
    if vmp_nom == 0.0:
        vmp_nom = _get_float(content, "VMppNom")
    vdc_max = _get_float(content, "VAbsMax")

    # ── 输出侧 ────────────────────────────────────────────────
    vac_out = _get_float(content, "VOutConv")
    pac_nom = _get_float(content, "PNomConv")   # kW
    pac_max = _get_float(content, "PMaxOUT")
    if pac_max == 0.0:
        pac_max = _get_float(content, "PMaxAC")
    iac_nom = _get_float(content, "INomAC")
    iac_max = _get_float(content, "IMaxAC")
    if iac_nom == 0.0 and vac_out > 0:
        iac_nom = round(pac_nom * 1000 / vac_out, 2)
    if iac_max == 0.0 and vac_out > 0:
        iac_max = round(pac_max * 1000 / vac_out, 2)

    # ── 效率 ──────────────────────────────────────────────────
    efficiency = _get_float(content, "EfficMax")
    if efficiency == 0.0:
        efficiency = _get_float(content, "EfficEuro")

    # ── 温度限制 ───────────────────────────────────────────────
    temp_pac_nom        = _get_float(content, "TPNom",    45.0)
    temp_pac_max        = _get_float(content, "TPMax",    35.0)
    temp_derating       = _get_float(content, "TPLim1",   60.0)
    temp_derating_limit = _get_float(content, "TPLimAbs", 62.0)
    pac_derating        = _get_float(content, "PLim1",     0.0)

    # ── 效率曲线（Point 单位为 W）─────────────────────────────
    efficiency_curves = _parse_efficiency_curves(content)

    # ── Sandia 参数（直读 + 精确拟合）────────────────────────
    sandia = _fit_sandia_params(content, pac_nom, efficiency_curves)

    return {
        "manufacturer":       manufacturer,
        "model_name":         model_name,
        "vmp_min":            vmp_min,
        "vmp_nom":            vmp_nom,
        "vmp_max":            vmp_max,
        "vdc_max":            vdc_max,
        "vac_out":            vac_out,
        "pac_nom":            pac_nom,
        "pac_max":            pac_max,
        "iac_nom":            iac_nom,
        "iac_max":            iac_max,
        "efficiency":         efficiency,
        "efficiency_curves":  efficiency_curves,
        "temp_pac_nom":       temp_pac_nom,
        "temp_pac_max":       temp_pac_max,
        "temp_derating":      temp_derating,
        "pac_derating":       pac_derating,
        "temp_derating_limit":temp_derating_limit,
        # ── Sandia 拟合参数 ────────────────────────────────────
        "p_aco": sandia["p_aco"],
        "p_dco": sandia["p_dco"],
        "p_so":  sandia["p_so"],
        "c_o":   sandia["c_o"],
    }
