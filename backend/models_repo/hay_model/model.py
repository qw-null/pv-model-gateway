import math

def _deg2rad(deg):
    return math.radians(deg)

def _cos_incidence(solar_zenith, solar_azimuth,
                   surface_tilt, surface_azimuth):
    Z  = _deg2rad(solar_zenith)
    S  = _deg2rad(surface_tilt)
    gs = _deg2rad(solar_azimuth)
    g  = _deg2rad(surface_azimuth)
    cos_theta = (
        math.cos(Z) * math.cos(S)
        + math.sin(Z) * math.sin(S) * math.cos(gs - g)
    )
    return max(0.0, cos_theta)

def run(inputs: dict) -> dict:
    ghi             = float(inputs["ghi"])
    dhi             = float(inputs["dhi"])
    bni             = float(inputs["bni"])
    solar_zenith    = float(inputs["solar_zenith"])
    solar_azimuth   = float(inputs["solar_azimuth"])
    surface_tilt    = float(inputs["surface_tilt"])
    surface_azimuth = float(inputs["surface_azimuth"])
    albedo          = float(inputs.get("albedo", 0.2))
    # 建议调用方传入当日修正值，而非固定使用太阳常数
    dni_extra       = float(inputs.get("dni_extra", 1367.0))

    S     = _deg2rad(surface_tilt)
    cos_z = math.cos(_deg2rad(solar_zenith))

    cos_theta = _cos_incidence(
        solar_zenith, solar_azimuth,
        surface_tilt, surface_azimuth
    )

    # 各向异性指数：BNI / E0（地外法向辐射）
    ai = bni / max(dni_extra, 1.0)
    ai = max(0.0, min(1.0, ai))

    # 倾斜比 Rb，加上合理上限防止数值爆炸
    rb = cos_theta / max(cos_z, 0.01)
    rb = min(rb, 10.0)  # ← 新增上限保护

    # 天空视角因子
    fsky = (1.0 + math.cos(S)) / 2.0

    bc = max(0.0, bni * cos_theta)
    dc = max(0.0, dhi * (ai * rb + (1.0 - ai) * fsky))
    dg = max(0.0, ghi * albedo * (1.0 - math.cos(S)) / 2.0)
    gti = max(0.0, bc + dc + dg)

    return {
        "gti": round(gti, 4),
        "bc":  round(bc,  4),
        "dc":  round(dc,  4),
        "dg":  round(dg,  4),
        "ai":  round(ai,  6),
    }
