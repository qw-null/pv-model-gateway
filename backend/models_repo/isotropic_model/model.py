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
    """
    各向同性转换模型（Liu-Jordan 1963）

    公式：
        Dc = DHI * (1 + cos(S)) / 2
        Dg = GHI * albedo * (1 - cos(S)) / 2
        Bc = BNI * cos(theta)
        GTI = Bc + Dc + Dg
    """
    ghi             = float(inputs["ghi"])
    dhi             = float(inputs["dhi"])
    bni             = float(inputs["bni"])
    solar_zenith    = float(inputs["solar_zenith"])
    solar_azimuth   = float(inputs["solar_azimuth"])
    surface_tilt    = float(inputs["surface_tilt"])
    surface_azimuth = float(inputs["surface_azimuth"])
    albedo          = float(inputs.get("albedo", 0.2))

    S = _deg2rad(surface_tilt)

    cos_theta = _cos_incidence(
        solar_zenith, solar_azimuth,
        surface_tilt, surface_azimuth
    )

    bc = max(0.0, bni * cos_theta)
    dc = max(0.0, dhi * (1.0 + math.cos(S)) / 2.0)
    dg = max(0.0, ghi * albedo * (1.0 - math.cos(S)) / 2.0)
    gti = max(0.0, bc + dc + dg)

    return {
        "gti": round(gti, 4),
        "bc":  round(bc,  4),
        "dc":  round(dc,  4),
        "dg":  round(dg,  4),
    }
