def run(inputs: dict) -> dict:
    import math

    L     = inputs["L"]
    delta = inputs["delta"]
    H     = inputs["H"]

    L_rad     = math.radians(L)
    delta_rad = math.radians(delta)
    H_rad     = math.radians(H)

    # 式(1)：sin α = cos L · cos δ · cos H + sin L · sin δ
    sin_alpha = (
        math.cos(L_rad) * math.cos(delta_rad) * math.cos(H_rad)
        + math.sin(L_rad) * math.sin(delta_rad)
    )
    sin_alpha = max(-1.0, min(1.0, sin_alpha))
    alpha_rad = math.asin(sin_alpha)
    alpha     = math.degrees(alpha_rad)

    # 式(2)：sin φs = -cos δ · sin H / cos α
    cos_alpha = math.cos(alpha_rad)
    if abs(cos_alpha) < 1e-9:
        phi_s = 0.0
    else:
        sin_phi_s = -math.cos(delta_rad) * math.sin(H_rad) / cos_alpha
        sin_phi_s = max(-1.0, min(1.0, sin_phi_s))
        phi_s_rad = math.asin(sin_phi_s)
        phi_s     = math.degrees(phi_s_rad)
        if math.cos(H_rad) < 0:
            phi_s = 180.0 - phi_s if phi_s >= 0 else -180.0 - phi_s

    Z = 90.0 - alpha

    return {
        "alpha":      round(alpha, 6),
        "phi_s":      round(phi_s, 6),
        "Z":          round(Z, 6),
        "is_daytime": alpha > 0,
    }
