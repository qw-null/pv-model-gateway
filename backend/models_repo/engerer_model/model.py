def run(inputs: dict) -> dict:
    import math

    kt         = inputs["kt"]
    ast        = inputs["ast"]
    Z          = inputs["solar_zenith"]
    ktc        = inputs["ktc"]
    ghi        = inputs["ghi"]
    ghc        = inputs["ghc"]
    model_type = inputs.get("model_type", "engerer2")

    # Δktc = ktc - kt
    delta_ktc = ktc - kt

    # kde = max(0, 1 - Ghc / Gh)（云增强项，仅 Engerer2 使用）
    if ghi > 0:
        k_de = max(0.0, 1.0 - ghc / ghi)
    else:
        k_de = 0.0

    # ── 模型系数表 ────────────────────────────────────────────────
    COEFFS = {
        #          C         β0        β1        β2          β3          β4        β5
        "engerer1": (0.1527,  -4.1092,  6.1661,  -2.2304e-3,  1.1026e-2, -4.3314,  None  ),
        "engerer2": (4.2336e-2,-3.7912, 7.5479,  -1.0036e-2,  3.1480e-3, -5.3146,  1.7073),
        "engerer3": (0.1090,  -2.0506e-2,8.1249, -3.6234e-2, -4.1397e-2, -5.1045,  None  ),
    }

    if model_type not in COEFFS:
        raise ValueError(f"不支持的模型类型: {model_type}，可选: engerer1/engerer2/engerer3")

    C, b0, b1, b2, b3, b4, b5 = COEFFS[model_type]

    # S 型函数内的线性组合
    linear = b0 + b1 * kt + b2 * ast + b3 * Z + b4 * delta_ktc

    # 防止 exp 溢出
    linear = max(-500.0, min(500.0, linear))

    # 式(7)/(8)/(7同结构): k = C + (1-C) / (1 + exp(linear))
    k = C + (1.0 - C) / (1.0 + math.exp(linear))

    # Engerer2 额外加线性校正项 β5 * kde（式8）
    if model_type == "engerer2" and b5 is not None:
        k = k + b5 * k_de

    k = max(0.0, min(1.0, k))

    # DHI = k * GHI
    dhi = k * ghi if ghi > 0 else 0.0

    # BNI = (GHI - DHI) / cos(Z)
    cos_z = math.cos(math.radians(Z))
    bni = (ghi - dhi) / cos_z if cos_z > 0.01 else 0.0

    return {
        "k":    round(k,    6),
        "dhi":  round(max(0.0, dhi), 4),
        "bni":  round(max(0.0, bni), 4),
        "k_de": round(k_de, 6),
    }
