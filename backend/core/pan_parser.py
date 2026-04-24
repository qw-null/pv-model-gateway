# backend/core/pan_parser.py
"""
解析 PVsyst .pan 文件（Version 8.x）
字段对照真实文件格式进行精确映射
"""
import re


def _get(content: str, key: str, default=None):
    """提取 key=value 格式的字段值（精确匹配行首）"""
    pattern = rf"(?m)^\s*{re.escape(key)}\s*=\s*(.+)$"
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


def _parse_iam(content: str) -> tuple:
    """
    解析 IAM 数据块，真实格式：
      NPtsEff=9
      Point_1=0.0,1.00000
      Point_2=20.0,1.00000
      ...
    提取 TCubicProfile 块内的数据点
    """
    angles, values = [], []

    # 提取 TCubicProfile 块
    block_match = re.search(
        r"IAMProfile=TCubicProfile(.+?)End of TCubicProfile",
        content,
        re.DOTALL
    )
    if not block_match:
        return angles, values

    block = block_match.group(1)

    # 提取所有 Point_N=angle,value
    points = re.findall(r"Point_\d+=\s*([\d.]+)\s*,\s*([\d.]+)", block)
    for angle_str, value_str in points:
        angles.append(float(angle_str))
        values.append(float(value_str))

    return angles, values


def parse_pan(content: str) -> dict:
    """
    解析 .pan 文件，返回与 PVPanel 数据库字段对应的字典

    PVsyst 尺寸单位说明：
      Width  = 短边（米）→ 对应组件宽度
      Height = 长边（米）→ 对应组件长度
      Depth  = 厚度（米）→ 需 ×1000 转换为 mm
    """
    # ── 基本信息 ──────────────────────────────────────────────
    manufacturer = _get_str(content, "Manufacturer")
    model_name   = _get_str(content, "Model")

    bifacial_factor_raw = _get_float(content, "BifacialityFactor", 0.0)
    bifacial_factor_pct = round(bifacial_factor_raw * 100, 2)
    is_bifacial  = bifacial_factor_raw > 0

    # ── 制造商规格 ─────────────────────────────────────────────
    isc        = _get_float(content, "Isc")
    voc        = _get_float(content, "Voc")
    imp        = _get_float(content, "Imp")     # 真实 key 是 Imp
    vmp        = _get_float(content, "Vmp")     # 真实 key 是 Vmp
    temp_coeff = _get_float(content, "muISC")   # mA/℃

    # ── 单二极管模型运行条件 ────────────────────────────────────
    g_ref = _get_float(content, "GRef", 1000.0)
    t_ref = _get_float(content, "TRef", 25.0)

    # 从 OperPoints 中提取 STC 工作点（Point_6 为 True 的行）
    # 格式：True,1000,25.0,0.00,Voc,Isc,Imp,Vmp,Pmp
    stc_match = re.search(
        r"Point_\d+=True,[\d.]+,[\d.]+,[\d.\-]+,"
        r"([\d.]+),([\d.]+),([\d.]+),([\d.]+),([\d.]+)",
        content
    )
    if stc_match:
        voc_calc = float(stc_match.group(1))
        isc_calc = float(stc_match.group(2))
        imp_calc = float(stc_match.group(3))
        vmp_calc = float(stc_match.group(4))
        pmp_calc = float(stc_match.group(5))
    else:
        # 兜底：直接使用制造商规格
        isc_calc = isc
        voc_calc = voc
        imp_calc = imp
        vmp_calc = vmp
        pmp_calc = round(imp * vmp, 4)

    # ── 尺寸（PVsyst 原始单位：米）────────────────────────────
    # Height = 长边（长度），Width = 短边（宽度），Depth = 厚度
    height_m    = _get_float(content, "Height")   # 长边，单位 m
    width_m     = _get_float(content, "Width")    # 短边，单位 m
    depth_m     = _get_float(content, "Depth")    # 厚度，单位 m

    length_mm   = round(height_m * 1000, 1)       # → mm
    width_mm    = round(width_m  * 1000, 1)       # → mm
    thickness_mm = round(depth_m * 1000, 1)       # → mm
    weight_kg   = _get_float(content, "Weight")
    area_m2     = round(height_m * width_m, 6)    # m²

    # ── 组件效率 ───────────────────────────────────────────────
    efficiency = 0.0
    if g_ref > 0 and area_m2 > 0:
        efficiency = round(pmp_calc / (g_ref * area_m2) * 100, 4)

    # ── IAM 数据 ───────────────────────────────────────────────
    iam_angles, iam_values = _parse_iam(content)

    return {
        "manufacturer":    manufacturer,
        "model_name":      model_name,
        "is_bifacial":     is_bifacial,
        "bifacial_factor": bifacial_factor_pct,

        "isc":             isc,
        "voc":             voc,
        "imp":             imp,
        "vmp":             vmp,
        "temp_coeff":      temp_coeff,

        "g_ref":           g_ref,
        "t_ref":           t_ref,
        "isc_calc":        isc_calc,
        "voc_calc":        voc_calc,
        "imp_calc":        imp_calc,
        "vmp_calc":        vmp_calc,
        "pmp_calc":        pmp_calc,
        "efficiency":      efficiency,

        "length":          length_mm,
        "width":           width_mm,
        "thickness":       thickness_mm,
        "weight":          weight_kg,
        "area":            area_m2,

        "iam_angles":      iam_angles,
        "iam_values":      iam_values,

        "r_series":     _get_float(content, "RSerie",  0.037),
        "r_shunt":      _get_float(content, "RShunt",  1000.0),
        "gamma":        _get_float(content, "Gamma",   1.255),
        "mu_voc_spec":  _get_float(content, "muVocSpec", -92.5),

    }
