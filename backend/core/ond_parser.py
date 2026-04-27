# backend/core/ond_parser.py
"""
解析 PVsyst .OND 文件（Version 6.x）
字段对照真实文件格式进行精确映射
"""
import re


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
    解析 TCubicProfile 块中的 Point_N=pin,pout 数据点
    真实格式：Point_1=40.0,0.0  (输入功率W, 输出功率W)
    过滤掉 pout=0 且 pin=0 的无效点，以及 pin=0 的起始点（除第一个点外）
    返回 (pin_list_kW, pout_list_kW, eta_list_pct)
    """
    points = re.findall(r"Point_\d+=\s*([\d.]+)\s*,\s*([\d.]+)", block)

    pin_list  = []
    pout_list = []
    eta_list  = []

    for pin_str, pout_str in points:
        pin  = float(pin_str)
        pout = float(pout_str)

        # 过滤无效点（pin=0 且 pout=0）
        if pin == 0.0 and pout == 0.0:
            continue

        pin_kw  = round(pin  / 1000, 6)
        pout_kw = round(pout / 1000, 6)

        # 计算效率（首个点 pin=0 时效率为0）
        eta = round(pout / pin * 100, 6) if pin > 0 else 0.0

        pin_list.append(pin_kw)
        pout_list.append(pout_kw)
        eta_list.append(eta)

    return pin_list, pout_list, eta_list


def _parse_efficiency_curves(content: str) -> dict:
    """
    解析三个电压档位的效率曲线
    真实格式：
      VNomEff=330.0,486.0,850.0,          ← 逗号分隔的电压档位
      ProfilPIOV1=TCubicProfile ... End    ← 低压档曲线
      ProfilPIOV2=TCubicProfile ... End    ← 中压档曲线
      ProfilPIOV3=TCubicProfile ... End    ← 高压档曲线
    """
    curves = {}

    # 解析电压档位列表
    v_line = _get(content, "VNomEff", "")
    voltages = [float(v.strip()) for v in v_line.split(",") if v.strip()]

    labels = ["low", "mid", "high"]

    for idx, profile_key in enumerate(["ProfilPIOV1", "ProfilPIOV2", "ProfilPIOV3"]):
        # 提取对应的 TCubicProfile 块
        block_match = re.search(
            rf"(?s){re.escape(profile_key)}=TCubicProfile(.+?)End of TCubicProfile",
            content
        )
        if not block_match:
            continue

        block = block_match.group(1)
        pin_list, pout_list, eta_list = _parse_profile_block(block)

        voltage = voltages[idx] if idx < len(voltages) else 0.0
        label   = labels[idx]

        curves[label] = {
            "voltage":   voltage,
            "pin_list":  pin_list,
            "pout_list": pout_list,
            "eta_list":  eta_list,
        }

    return curves


def parse_ond(content: str) -> dict:
    """
    解析 .OND 文件，返回与 Inverter 数据库字段对应的字典
    """
    # ── 基本信息 ──────────────────────────────────────────────
    manufacturer = _get_str(content, "Manufacturer")
    model_name   = _get_str(content, "Model")

    # ── 输入侧（注意大小写兼容）────────────────────────────────
    vmp_min = _get_float(content, "VMppMin")
    vmp_max = _get_float(content, "VMPPMax")   # 真实文件大写 MPPP
    if vmp_max == 0.0:
        vmp_max = _get_float(content, "VMppMax")
    vmp_nom = _get_float(content, "VmppNom")   # 真实文件小写 mpp
    if vmp_nom == 0.0:
        vmp_nom = _get_float(content, "VMppNom")
    vdc_max = _get_float(content, "VAbsMax")

    # ── 输出侧 ────────────────────────────────────────────────
    vac_out = _get_float(content, "VOutConv")

    # 真实文件中功率单位已是 kW
    pac_nom = _get_float(content, "PNomConv")   # 8.000 kW
    pac_max = _get_float(content, "PMaxOUT")    # 8.800 kW
    if pac_max == 0.0:
        pac_max = _get_float(content, "PMaxAC")

    # 直接读取电流（比计算更准确）
    iac_nom = _get_float(content, "INomAC")     # 11.5 A
    iac_max = _get_float(content, "IMaxAC")     # 13.3 A

    # 兜底：若文件无电流字段则计算
    if iac_nom == 0.0 and vac_out > 0:
        iac_nom = round(pac_nom * 1000 / vac_out, 2)
    if iac_max == 0.0 and vac_out > 0:
        iac_max = round(pac_max * 1000 / vac_out, 2)

    # ── 效率（真实文件已是百分比，无需×100）──────────────────
    efficiency = _get_float(content, "EfficMax")    # 98.00
    if efficiency == 0.0:
        efficiency = _get_float(content, "EfficEuro")  # 97.60

    # ── 输出参数（温度限制，功率单位已是 kW）─────────────────
    temp_pac_nom        = _get_float(content, "TPNom",    45.0)
    temp_pac_max        = _get_float(content, "TPMax",    35.0)
    temp_derating       = _get_float(content, "TPLim1",   60.0)
    temp_derating_limit = _get_float(content, "TPLimAbs", 62.0)
    pac_derating        = _get_float(content, "PLim1",     0.0)  # 3.000 kW，直接使用

    # ── 效率曲线（三个电压档位）────────────────────────────────
    efficiency_curves = _parse_efficiency_curves(content)

    return {
        "manufacturer":        manufacturer,
        "model_name":          model_name,
        "vmp_min":             vmp_min,
        "vmp_nom":             vmp_nom,
        "vmp_max":             vmp_max,
        "vdc_max":             vdc_max,
        "vac_out":             vac_out,
        "pac_nom":             pac_nom,
        "pac_max":             pac_max,
        "iac_nom":             iac_nom,
        "iac_max":             iac_max,
        "efficiency":          efficiency,
        "efficiency_curves":   efficiency_curves,
        "temp_pac_nom":        temp_pac_nom,
        "temp_pac_max":        temp_pac_max,
        "temp_derating":       temp_derating,
        "pac_derating":        pac_derating,
        "temp_derating_limit": temp_derating_limit,
    }
