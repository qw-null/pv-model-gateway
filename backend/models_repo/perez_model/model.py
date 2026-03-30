import math


# ══════════════════════════════════════════════════════════════
# Perez 系数表（F11, F12, F13, F21, F22, F23）
# 按 epsilon 分 8 档
# ══════════════════════════════════════════════════════════════
PEREZ_COEFFICIENTS = {
    1: [-0.0083117,  0.5877285, -0.0620636, -0.0596012,  0.0721249, -0.0220216],
    2: [ 0.1299457,  0.6825954, -0.1513752, -0.0189325,  0.0659650, -0.0288748],
    3: [ 0.3296958,  0.4868735, -0.2210958,  0.0554140, -0.0639588, -0.0260542],
    4: [ 0.5682053,  0.1874525, -0.2951290,  0.1088162, -0.1519229, -0.0139754],
    5: [ 0.8730280, -0.3920403, -0.3616149,  0.2261818, -0.4620442,  0.0012448],
    6: [ 1.1326077, -1.2367284, -0.4118494,  0.2877220, -0.8230357,  0.0558651],
    7: [ 1.0601591, -1.5999137, -0.3589221,  0.2642124, -1.1272340,  0.1310694],
    8: [ 0.6777470, -0.3272588, -0.2504286,  0.1561313, -1.3765031,  0.2506212],
}

EPSILON_BINS = [1.065, 1.23, 1.5, 1.95, 2.8, 4.5, 6.2, float("inf")]


def _deg2rad(deg):
    return math.radians(deg)


def _cos_incidence(solar_zenith, solar_azimuth,
                   surface_tilt, surface_azimuth):
    Z  = _deg2rad(solar_zenith)
    S  = _deg2rad(surface_tilt)
    gs = _deg2rad(solar_azimuth)
    g  = _deg2rad(surface_azimuth)
    return max(0.0,
        math.cos(Z) * math.cos(S)
        + math.sin(Z) * math.sin(S) * math.cos(gs - g)
    )


def _epsilon(dhi, bni, solar_zenith, kappa=1.041):
    Z = _deg2rad(solar_zenith)
    if dhi < 1e-6:
        return 1.0
    num = (dhi + bni) / dhi + kappa * Z ** 3
    den = 1.0 + kappa * Z ** 3
    return num / den


def _delta(dhi, dni_extra, solar_zenith):
    cos_z = math.cos(_deg2rad(solar_zenith))
    if cos_z < 0.01:
        return 0.0
    return dhi / (max(dni_extra, 1.0) * cos_z)


def _epsilon_bin(eps):
    for i, upper in enumerate(EPSILON_BINS):
        if eps < upper:
            return i + 1
    return 8


def _f1f2(eps, delta, solar_zenith):
    Z    = _deg2rad(solar_zenith)
    ebin = _epsilon_bin(eps)
    cf   = PEREZ_COEFFICIENTS[ebin]
    f1   = max(0.0, cf[0] + cf[1] * delta + cf[2] * Z)
    f2   =          cf[3] + cf[4] * delta + cf[5] * Z
    return f1, f2


def run(inputs: dict) -> dict:
    """
    Perez 系列转换模型（1986 / 1987 / 1988 / 1990a / 1990b）

    核心公式（1987/1988/1990 共用）：
        Dc = DHI * [(1-F1)*Fsky + F1*(a/b) + F2*sin(S)]

    其中：
        Fsky = (1+cos(S))/2
        a    = max(0, cos(theta))
        b    = max(cos(85°), cos(Z))   Perez1987
        b    = max(0.087, cos(Z))      Perez1988/1990

    Perez1986 使用简化 F1/F2 估算（不查表）。
    Perez1990b 使用 Perez1987 公式 + 1990 epsilon 系数。
    """
    ghi             = float(inputs["ghi"])
    dhi             = float(inputs["dhi"])
    bni             = float(inputs["bni"])
    solar_zenith    = float(inputs["solar_zenith"])
    solar_azimuth   = float(inputs["solar_azimuth"])
    surface_tilt    = float(inputs["surface_tilt"])
    surface_azimuth = float(inputs["surface_azimuth"])
    albedo          = float(inputs.get("albedo", 0.2))
    dni_extra       = float(inputs.get("dni_extra", 1367.0))
    model_type      = inputs.get("model_type", "perez1990a")

    S     = _deg2rad(surface_tilt)
    cos_z = math.cos(_deg2rad(solar_zenith))
    fsky  = (1.0 + math.cos(S)) / 2.0

    cos_theta = _cos_incidence(
        solar_zenith, solar_azimuth,
        surface_tilt, surface_azimuth
    )

    eps   = _epsilon(dhi, bni, solar_zenith)
    delta = _delta(dhi, dni_extra, solar_zenith)

    # ── 按版本计算 F1/F2 和 a/b ──────────────────────────────

    if model_type == "perez1986":
        # 简化估算，不查系数表
        f1 = max(0.0, 0.9 * delta)
        f2 = 0.45 * delta - 0.1
        a  = max(0.0, cos_theta)
        b  = max(0.087, cos_z)

    elif model_type in ("perez1987", "perez1990b"):
        # 查表，b 使用 cos(85°)
        f1, f2 = _f1f2(eps, delta, solar_zenith)
        a = max(0.0, cos_theta)
        b = max(math.cos(_deg2rad(85.0)), cos_z)

    elif model_type in ("perez1988", "perez1990a"):
        # 查表，b 使用 0.087（点光源简化）
        f1, f2 = _f1f2(eps, delta, solar_zenith)
        a = max(0.0, cos_theta)
        b = max(0.087, cos_z)

    else:
        raise ValueError(
            f"model_type 不合法：'{model_type}'，"
            f"允许值为 perez1986/perez1987/perez1988/perez1990a/perez1990b"
        )

    # ── 计算各分量 ────────────────────────────────────────────
    bc  = max(0.0, bni * cos_theta)
    dc  = max(0.0, dhi * ((1.0 - f1) * fsky + f1 * (a / b) + f2 * math.sin(S)))
    dg  = max(0.0, ghi * albedo * (1.0 - math.cos(S)) / 2.0)
    gti = max(0.0, bc + dc + dg)

    return {
        "gti":     round(gti,   4),
        "bc":      round(bc,    4),
        "dc":      round(dc,    4),
        "dg":      round(dg,    4),
        "f1":      round(f1,    6),
        "f2":      round(f2,    6),
        "epsilon": round(eps,   6),
        "delta":   round(delta, 6),
    }
