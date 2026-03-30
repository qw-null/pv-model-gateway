def run(inputs: dict) -> dict:
    import math

    kt         = inputs["kt"]
    ast        = inputs["ast"]
    Z          = inputs["solar_zenith"]
    ktc        = inputs["ktc"]
    ghi        = inputs["ghi"]
    ghc        = inputs["ghc"]
    k_ext      = inputs["k_ext"]       # k_s 或 k_hourly_engerer2
    model_type = inputs.get("model_type", "yang4")
    cluster    = int(inputs.get("cluster", 1))

    # ── 公共中间量 ────────────────────────────────────────────────
    delta_ktc = ktc - kt
    k_de      = max(0.0, 1.0 - ghc / ghi) if ghi > 0 else 0.0

    # ── 系数定义 ──────────────────────────────────────────────────
    # Yang1: 式(9)  k = C + L/(1+exp(linear)) + β5*kde + β6*k_s
    # Yang2: 式(10) k = C + (1-C)/(1+exp(linear + β6*k_s)) + β5*kde
    # Yang3: 式(11) 同 Yang1 结构，k_ext = k_hourly_Engerer2
    # Yang4: 式(12) 同 Yang2 结构，k_ext = k_hourly_Engerer2
    # Yang5: 式(12) 同 Yang4 结构，系数按 cluster 动态选取

    # Yang1/Yang3 共享系数（L 参数）
    YANG13_COEFFS = {
        # C       β0       β1      β2       β3       β4       β5      β6      L
        "yang1": (0.0369, -3.4986, 7.9735, -0.0030,  0.0031, -7.6836, 1.0179, 0.3505, 0.6768),
        "yang3": (0.0369, -3.4986, 7.9735, -0.0030,  0.0031, -7.6836, 1.0179, 0.3505, 0.6768),
    }

    # Yang2/Yang4 共享系数
    YANG24_COEFFS = {
        # C       β0       β1      β2       β3       β4       β5      β6
        "yang2": (0.0361, -0.5744, 4.3184, -0.0011,  0.0004, -4.7952, 1.4414, -2.8396),
        "yang4": (0.0361, -0.5744, 4.3184, -0.0011,  0.0004, -4.7952, 1.4414, -2.8396),
    }

    # Yang5 动态系数（按气候分区）
    YANG5_COEFFS = {
        # cluster: (C, β0, β1, β2, β3, β4, β5, β6)
        1: (0.13105, -4.36740, 7.68051,  0.00540,  0.01748,  0.91590, 0.52176, -1.68819),
        2: (-0.01014,-3.33038, 5.72327,  0.01296,  0.01230, -0.96483, 0.94204, -1.68332),
        3: (-0.27475, 0.36085, 0.39860,  0.00479,  0.00039,-10.20264, 2.12475, -1.78455),
        4: (-0.01095,-0.92129, 3.65015,  0.00767,  0.00494, -3.76465, 1.36482, -2.11867),
        5: (0.04297, -1.64437, 4.71808,  0.01462,  0.00745, -3.35223, 1.25192, -2.36477),
    }

    # ── 计算 k ────────────────────────────────────────────────────
    if model_type in ("yang1", "yang3"):
        C, b0, b1, b2, b3, b4, b5, b6, L = YANG13_COEFFS[model_type]
        linear = b0 + b1*kt + b2*ast + b3*Z + b4*delta_ktc
        linear = max(-500.0, min(500.0, linear))
        # 式(9): k = C + L/(1+exp(linear)) + β5*kde + β6*k_ext
        k = C + L / (1.0 + math.exp(linear)) + b5 * k_de + b6 * k_ext

    elif model_type in ("yang2", "yang4"):
        C, b0, b1, b2, b3, b4, b5, b6 = YANG24_COEFFS[model_type]
        linear = b0 + b1*kt + b2*ast + b3*Z + b4*delta_ktc + b6*k_ext
        linear = max(-500.0, min(500.0, linear))
        # 式(10)/(12): k = C + (1-C)/(1+exp(linear)) + β5*kde
        k = C + (1.0 - C) / (1.0 + math.exp(linear)) + b5 * k_de

    elif model_type == "yang5":
        if cluster not in YANG5_COEFFS:
            raise ValueError(f"cluster 必须为 1~5，当前传入: {cluster}")
        C, b0, b1, b2, b3, b4, b5, b6 = YANG5_COEFFS[cluster]
        linear = b0 + b1*kt + b2*ast + b3*Z + b4*delta_ktc + b6*k_ext
        linear = max(-500.0, min(500.0, linear))
        # 与 Yang4 结构一致
        k = C + (1.0 - C) / (1.0 + math.exp(linear)) + b5 * k_de

    else:
        raise ValueError(f"不支持的模型类型: {model_type}")

    k = max(0.0, min(1.0, k))

    # DHI = k * GHI
    dhi = k * ghi if ghi > 0 else 0.0

    # BNI = (GHI - DHI) / cos(Z)
    cos_z = math.cos(math.radians(Z))
    bni = (ghi - dhi) / cos_z if cos_z > 0.01 else 0.0

    return {
        "k":   round(k,   6),
        "dhi": round(max(0.0, dhi), 4),
        "bni": round(max(0.0, bni), 4),
    }
