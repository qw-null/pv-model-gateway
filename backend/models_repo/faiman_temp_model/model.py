# ══════════════════════════════════════════════════════════════
# SAM 安装方式 NOCT 修正量
# ══════════════════════════════════════════════════════════════
NOCT_CORRECTION = {
    "rack":          0,
    "2.5_to_3.5in":  2,
    "1.5_to_2.5in":  6,
    "0.5_to_1.5in": 11,
    "less_0.5in":   18,
}

# SAM 建筑高度风速修正系数
WIND_CORRECTION = {
    "low":  0.51,
    "high": 0.61,
}


def _faiman(tamb, gc, wind_speed, u0, u1):
    """
    Faiman 模型（式50）
    Tmod = Tamb + Gc / (u0 + u1*W)
    """
    denominator = u0 + u1 * wind_speed
    if denominator <= 0:
        denominator = 1e-6
    return tamb + gc / denominator


def _pvsyst(tamb, gc, wind_speed, u0, u1, eta_amb, alpha):
    """
    PVSyst 模型（式51）
    Tmod = Tamb + Gc * (alpha - eta_amb) / (u0 + u1*W)
    """
    denominator = u0 + u1 * wind_speed
    if denominator <= 0:
        denominator = 1e-6
    return tamb + gc * (alpha - eta_amb) / denominator


def _mattei(tamb, gc, wind_speed,
            eta_mpp_ref, gamma_pmpp, tau_alpha):
    """
    Mattei 模型（式52）
    将光伏效率模型整合到热能平衡

    Upv = 26.6 + 2.3 * W
    Tmod = (Upv*Ta + Gc*[τα - η_mpp_ref*(1 - 25*γ)]) / (Upv + γ*η_mpp_ref*Gc)
    """
    upv = 26.6 + 2.3 * wind_speed

    numerator = (
        upv * tamb
        + gc * (tau_alpha - eta_mpp_ref * (1.0 - 25.0 * gamma_pmpp))
    )
    denominator = upv + gamma_pmpp * eta_mpp_ref * gc

    if abs(denominator) < 1e-9:
        return tamb

    return numerator / denominator


def _sam(tamb, gc, wind_speed, noct, mounting_type, building_height):
    """
    SAM 模型（式53~54）

    NOCT' = NOCT + 安装方式修正量
    W'    = 建筑高度修正系数 * W
    Tcell = Tamb + Gc/800 * (NOCT' - 20) * (1 - W'/...）

    SAM 完整公式：
    Tcell = Tamb + (NOCT' - 20) / 800 * Gc * (9.5 / (5.7 + 3.8*W'))
    """
    noct_corr  = NOCT_CORRECTION.get(mounting_type, 0)
    wind_coeff = WIND_CORRECTION.get(building_height, 0.51)

    noct_prime = noct + noct_corr
    wind_prime = wind_coeff * wind_speed

    # SAM 完整公式
    heat_transfer = 9.5 / (5.7 + 3.8 * wind_prime)
    t_cell = tamb + (noct_prime - 20.0) / 800.0 * gc * heat_transfer

    return t_cell, noct_prime, wind_prime


def run(inputs: dict) -> dict:
    """
    Faiman / PVSyst / Mattei / SAM 电池温度模型（模型28~30）

    faiman（式50）：Tmod = Tamb + Gc / (u0 + u1*W)
    pvsyst（式51）：Tmod = Tamb + Gc*(α-η_amb) / (u0 + u1*W)
    mattei（式52）：整合光伏效率与热能平衡
    sam  （式53）：基于 NOCT 的 SAM 模型，含安装方式和建筑高度修正
    """
    tamb         = float(inputs["tamb"])
    gc           = float(inputs["gc"])
    wind_speed   = float(inputs["wind_speed"])
    model_type   = inputs.get("model_type", "faiman")

    noct_prime = None
    wind_prime = None

    if model_type == "faiman":
        u0     = float(inputs.get("u0", 25.0))
        u1     = float(inputs.get("u1", 6.84))
        t_cell = _faiman(tamb, gc, wind_speed, u0, u1)

    elif model_type == "pvsyst":
        u0      = float(inputs.get("u0",      25.0))
        u1      = float(inputs.get("u1",       6.84))
        eta_amb = float(inputs.get("eta_amb",  0.1))
        alpha   = float(inputs.get("alpha",    0.9))
        t_cell  = _pvsyst(tamb, gc, wind_speed, u0, u1, eta_amb, alpha)

    elif model_type == "mattei":
        eta_mpp_ref  = float(inputs.get("eta_mpp_ref",  0.15))
        gamma_pmpp   = float(inputs.get("gamma_pmpp",  -0.004))
        tau_alpha    = float(inputs.get("tau_alpha",    0.81))
        t_cell       = _mattei(
            tamb, gc, wind_speed,
            eta_mpp_ref, gamma_pmpp, tau_alpha
        )

    elif model_type == "sam":
        noct           = float(inputs.get("noct", 45.0))
        mounting_type  = inputs.get("mounting_type",  "rack")
        building_height = inputs.get("building_height", "low")
        t_cell, noct_prime, wind_prime = _sam(
            tamb, gc, wind_speed,
            noct, mounting_type, building_height
        )

    else:
        raise ValueError(
            f"model_type 不合法：'{model_type}'，"
            f"允许值为 faiman / pvsyst / mattei / sam"
        )

    return {
        "t_cell":      round(t_cell,                    4),
        "noct_prime":  round(noct_prime, 4) if noct_prime is not None else None,
        "wind_prime":  round(wind_prime, 4) if wind_prime is not None else None,
    }
