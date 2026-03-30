import math


def _deg2rad(deg):
    return math.radians(deg)


def _rad2deg(rad):
    return math.degrees(rad)


def _fresnel_transmittance(theta_i_rad, n1, n2):
    """
    基于 Fresnel 定律计算界面透过率（不考虑吸收）

    τ_fresnel = 1 - (Rs + Rp) / 2

    其中：
        Rs = ((n1*cos(θi) - n2*cos(θr)) / (n1*cos(θi) + n2*cos(θr)))²
        Rp = ((n1*cos(θr) - n2*cos(θi)) / (n1*cos(θr) + n2*cos(θi)))²

    Snell 定律：n1*sin(θi) = n2*sin(θr)
    """
    sin_i = math.sin(theta_i_rad)
    sin_r = (n1 / n2) * sin_i

    # 全内反射检查
    if abs(sin_r) > 1.0:
        return 0.0, 90.0

    theta_r_rad = math.asin(sin_r)
    cos_i = math.cos(theta_i_rad)
    cos_r = math.cos(theta_r_rad)

    # s 偏振反射率
    num_s = n1 * cos_i - n2 * cos_r
    den_s = n1 * cos_i + n2 * cos_r
    Rs = (num_s / den_s) ** 2 if den_s != 0 else 1.0

    # p 偏振反射率
    num_p = n2 * cos_i - n1 * cos_r
    den_p = n2 * cos_i + n1 * cos_r
    Rp = (num_p / den_p) ** 2 if den_p != 0 else 1.0

    tau_fresnel = 1.0 - (Rs + Rp) / 2.0
    return max(0.0, tau_fresnel), _rad2deg(theta_r_rad)


def run(inputs: dict) -> dict:
    """
    基于物理模型的光束透过率模型（式42）

    同时考虑：
    1. 界面 Fresnel 反射损耗（两个界面：空气→玻璃，玻璃→封装）
    2. 玻璃内部 Beer-Lambert 吸收损耗

    公式：
        τ_reflect = τ_fresnel(θi, n1, n2) × τ_fresnel(θr, n2, n1)
        τ_absorb  = exp(-K × L / cos(θr))
        τb = τ_reflect × τ_absorb

    其中：
        θi：入射角（AOI）
        θr：折射角（Snell 定律）
        K：消光系数（m⁻¹）
        L：玻璃厚度（m）
    """
    bc  = float(inputs["bc"])
    aoi = float(inputs["aoi"])
    n1  = float(inputs.get("n1",  1.0))
    n2  = float(inputs.get("n2",  1.526))
    K   = float(inputs.get("K",   4.0))
    L   = float(inputs.get("L",   0.002))

    theta_i_rad = _deg2rad(aoi)

    # ── 界面1：空气 → 玻璃 ───────────────────────────────────
    tau_f1, theta_r_deg = _fresnel_transmittance(theta_i_rad, n1, n2)
    theta_r_rad = _deg2rad(theta_r_deg)

    # ── 界面2：玻璃 → 封装（近似 n2 → n1 的逆过程）────────────
    tau_f2, _ = _fresnel_transmittance(theta_r_rad, n2, n1)

    # ── 反射损耗综合透过率 ────────────────────────────────────
    tau_reflection = tau_f1 * tau_f2

    # ── 玻璃内部吸收（Beer-Lambert 定律）────────────────────
    cos_r = math.cos(theta_r_rad) if theta_r_deg < 90.0 else 1e-6
    tau_absorption = math.exp(-K * L / max(cos_r, 1e-6))

    # ── 综合透过率 τb ─────────────────────────────────────────
    tau_b = tau_reflection * tau_absorption
    tau_b = max(0.0, min(1.0, tau_b))

    # ── 有效直接辐照度 ────────────────────────────────────────
    geff_b = tau_b * bc

    return {
        "tau_b":            round(tau_b,            6),
        "tau_b_reflection": round(tau_reflection,   6),
        "tau_b_absorption": round(tau_absorption,   6),
        "theta_r":          round(theta_r_deg,      4),
        "geff_b":           round(geff_b,           4),
    }
