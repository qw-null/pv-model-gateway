import math


def _deg2rad(deg):
    return math.radians(deg)


def _fresnel_tau(theta_i_rad, n1, n2, K, L):
    """
    单方向 Fresnel + Beer-Lambert 综合透过率

    τ(θi) = τ_fresnel(θi) × exp(-K*L/cos(θr))
    """
    sin_i = math.sin(theta_i_rad)
    sin_r_val = (n1 / n2) * sin_i

    if abs(sin_r_val) >= 1.0:
        return 0.0

    theta_r_rad = math.asin(sin_r_val)
    cos_i = math.cos(theta_i_rad)
    cos_r = math.cos(theta_r_rad)

    # Fresnel 反射率
    num_s = n1 * cos_i - n2 * cos_r
    den_s = n1 * cos_i + n2 * cos_r
    Rs = (num_s / den_s) ** 2 if abs(den_s) > 1e-9 else 1.0

    num_p = n2 * cos_i - n1 * cos_r
    den_p = n2 * cos_i + n1 * cos_r
    Rp = (num_p / den_p) ** 2 if abs(den_p) > 1e-9 else 1.0

    tau_fresnel = 1.0 - (Rs + Rp) / 2.0

    # Beer-Lambert 吸收
    tau_absorb = math.exp(-K * L / max(cos_r, 1e-6))

    return max(0.0, tau_fresnel * tau_absorb)


def _integrate_tau_hemisphere(n1, n2, K, L, n_steps=90):
    """
    对半球方向（0°~90°）按 cos(θ) 加权数值积分，得到漫射平均透过率

    τd = ∫₀^(π/2) τ(θ) × sin(θ) × cos(θ) dθ  /  ∫₀^(π/2) sin(θ) × cos(θ) dθ

    分母 = 0.5（各向同性归一化）
    """
    numerator   = 0.0
    denominator = 0.0
    d_theta = (math.pi / 2.0) / n_steps

    for i in range(n_steps):
        theta = (i + 0.5) * d_theta
        weight = math.sin(theta) * math.cos(theta) * d_theta
        tau    = _fresnel_tau(theta, n1, n2, K, L)
        numerator   += tau * weight
        denominator += weight

    return numerator / denominator if denominator > 1e-9 else 0.0


def _integrate_tau_ground(surface_tilt_deg, n1, n2, K, L, n_steps=90):
    """
    地面反射辐射透过率 τg

    地面反射辐射来自组件下方（θ 从 90°-S 到 90°），
    按 Xie 2022 方法，等效入射角范围为 (90°-S/2) 附近，
    采用数值积分对地面可见半球加权。

    τg = ∫ τ(θ) × sin(θ) × cos(θ) dθ  /  ∫ sin(θ) × cos(θ) dθ
    积分范围：θ ∈ [90°-S, 90°]（地面反射的入射角范围）
    """
    S = _deg2rad(surface_tilt_deg)
    theta_min = math.pi / 2.0 - S
    theta_max = math.pi / 2.0

    if theta_min >= theta_max:
        return 0.0

    numerator   = 0.0
    denominator = 0.0
    d_theta = (theta_max - theta_min) / n_steps

    for i in range(n_steps):
        theta  = theta_min + (i + 0.5) * d_theta
        weight = math.sin(theta) * math.cos(theta) * d_theta
        tau    = _fresnel_tau(theta, n1, n2, K, L)
        numerator   += tau * weight
        denominator += weight

    return numerator / denominator if denominator > 1e-9 else 0.0


def run(inputs: dict) -> dict:
    """
    Xie 等人 2022 年提出的漫射/地面反射透过率解析模型

    τd（式43）：
        对天空半球方向按 Fresnel+Beer-Lambert 加权积分，
        得到漫射辐射的平均透过率

    τg（式45）：
        对地面反射可见方向按 Fresnel+Beer-Lambert 加权积分，
        考虑倾斜角 S 决定的地面可见范围

    有效辐照度：
        Geff_d = τd × Dc
        Geff_g = τg × Dg
    """
    dc           = float(inputs["dc"])
    dg           = float(inputs["dg"])
    surface_tilt = float(inputs["surface_tilt"])
    n1           = float(inputs.get("n1",  1.0))
    n2           = float(inputs.get("n2",  1.526))
    K            = float(inputs.get("K",   4.0))
    L            = float(inputs.get("L",   0.002))

    # ── τd：天空漫射半球积分 ──────────────────────────────────
    tau_d = _integrate_tau_hemisphere(n1, n2, K, L)

    # ── τg：地面反射方向积分 ──────────────────────────────────
    tau_g = _integrate_tau_ground(surface_tilt, n1, n2, K, L)

    # ── 有效辐照度 ────────────────────────────────────────────
    geff_d = tau_d * dc
    geff_g = tau_g * dg

    return {
        "tau_d":  round(tau_d,  6),
        "tau_g":  round(tau_g,  6),
        "geff_d": round(geff_d, 4),
        "geff_g": round(geff_g, 4),
    }
