import math


def _deg2rad(deg):
    return math.radians(deg)


def run(inputs: dict) -> dict:
    """
    Martin & Ruiz 2001 半经验反射损失模型

    公式：
        τb = 1 - exp(-cos(AOI) / ar)          式(39) 直接辐射透过率
        τd = 1 - exp(-c1 / ar)                 式(40) 漫射辐射透过率
        τg = 1 - exp(-cos(90°-S/2) / ar)       式(41) 地面反射透过率

    其中：
        c1 = 4/(3π) ≈ 0.4244
        ar：封装反射系数（与组件封装设计相关）

    有效吸收辐照度：
        Geff = τb * Bc + τd * Dc + τg * Dg
    """
    bc           = float(inputs["bc"])
    dc           = float(inputs["dc"])
    dg           = float(inputs["dg"])
    aoi          = float(inputs["aoi"])
    surface_tilt = float(inputs["surface_tilt"])
    ar           = float(inputs.get("ar", 0.16))
    c1           = float(inputs.get("c1", 4.0 / (3.0 * math.pi)))

    # ── 直接辐射透过率 τb ────────────────────────────────────
    # τb = 1 - exp(-cos(AOI) / ar)
    cos_aoi = math.cos(_deg2rad(aoi))
    tau_b = 1.0 - math.exp(-cos_aoi / ar) if ar > 0 else 1.0
    tau_b = max(0.0, min(1.0, tau_b))

    # ── 漫射辐射透过率 τd ────────────────────────────────────
    # τd = 1 - exp(-c1 / ar)
    tau_d = 1.0 - math.exp(-c1 / ar) if ar > 0 else 1.0
    tau_d = max(0.0, min(1.0, tau_d))

    # ── 地面反射辐射透过率 τg ────────────────────────────────
    # 等效入射角为 (90° - S/2)，即地面反射的平均入射角
    S = surface_tilt
    aoi_g = 90.0 - S / 2.0
    cos_aoi_g = math.cos(_deg2rad(aoi_g))
    tau_g = 1.0 - math.exp(-cos_aoi_g / ar) if ar > 0 else 1.0
    tau_g = max(0.0, min(1.0, tau_g))

    # ── 有效吸收辐照度 Geff ──────────────────────────────────
    geff = tau_b * bc + tau_d * dc + tau_g * dg
    geff = max(0.0, geff)

    return {
        "tau_b": round(tau_b, 6),
        "tau_d": round(tau_d, 6),
        "tau_g": round(tau_g, 6),
        "geff":  round(geff,  4),
    }
