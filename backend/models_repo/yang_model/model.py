import math


# ══════════════════════════════════════════════════════════════
# Yang1 系数（固定）
# 公式：k = C + L/(1+exp(...)) + B5*kde + B6*k_s
# ══════════════════════════════════════════════════════════════
YANG1_COEF = {
    "C":  0.0369,
    "L":  0.6768,
    "B0": -3.4986,
    "B1":  7.9735,
    "B2": -0.0030,
    "B3":  0.0031,
    "B4": -7.6836,
    "B5":  1.0179,
    "B6":  0.3505,
}

# ══════════════════════════════════════════════════════════════
# Yang2 系数（固定）
# 公式：k = C + (1-C)/(1+exp(...+B6*k_s)) + B5*kde
# ══════════════════════════════════════════════════════════════
YANG2_COEF = {
    "C":  0.0361,
    "B0": -0.5744,
    "B1":  4.3184,
    "B2": -0.0011,
    "B3":  0.0004,
    "B4": -4.7952,
    "B5":  1.4414,
    "B6": -2.8396,
}

# ══════════════════════════════════════════════════════════════
# Yang3/4 系数（与 Yang2 一致）
# Yang3 公式同 Yang1（L 版本），用 k_hourly 替代 k_s
# Yang4 公式同 Yang2，用 k_hourly 替代 k_s
# ══════════════════════════════════════════════════════════════
YANG3_COEF = YANG1_COEF   # 结构同 Yang1，k_s 换成 k_hourly_engerer2
YANG4_COEF = YANG2_COEF   # 结构同 Yang2，k_s 换成 k_hourly_engerer2

# ══════════════════════════════════════════════════════════════
# Yang5 系数（按辐射气候分区动态选取，结构同 Yang4）
# ══════════════════════════════════════════════════════════════
YANG5_CLUSTER_COEF = {
    "1": {
        "C":  0.13105,
        "B0": -4.36740,
        "B1":  7.68051,
        "B2":  0.00540,
        "B3":  0.01748,
        "B4":  0.91590,
        "B5":  0.52176,
        "B6": -1.68819,
    },
    "2": {
        "C": -0.01014,
        "B0": -3.33038,
        "B1":  5.72327,
        "B2":  0.01296,
        "B3":  0.01230,
        "B4": -0.96483,
        "B5":  0.94204,
        "B6": -1.68332,
    },
    "3": {
        "C": -0.27475,
        "B0":  0.36085,
        "B1":  0.39860,
        "B2":  0.00479,
        "B3":  0.00039,
        "B4": -10.20264,
        "B5":  2.12475,
        "B6": -1.78455,
    },
    "4": {
        "C": -0.01095,
        "B0": -0.92129,
        "B1":  3.65015,
        "B2":  0.00767,
        "B3":  0.00494,
        "B4": -3.76465,
        "B5":  1.36482,
        "B6": -2.11867,
    },
    "5": {
        "C":  0.04297,
        "B0": -1.64437,
        "B1":  4.71808,
        "B2":  0.01462,
        "B3":  0.00745,
        "B4": -3.35223,
        "B5":  1.25192,
        "B6": -2.36477,
    },
}


def _compute_kde(ghi: float, ghc: float) -> float:
    """云增强漫射比例 kde = max(0, 1 - Ghc/Ghi)"""
    if ghi > 0:
        return max(0.0, 1.0 - ghc / ghi)
    return 0.0


def _safe_exp(x: float) -> float:
    """防止指数溢出"""
    return math.exp(max(-500.0, min(500.0, x)))


def _yang_type1(coef: dict, kt, ast, z, delta_ktc, kde, k_extra) -> float:
    """
    Yang1 / Yang3 公式结构（L 版本）：
        k = C + L / (1 + exp(B0 + B1*kt + B2*AST + B3*Z + B4*Δktc))
              + B5*kde + B6*k_extra
    """
    C  = coef["C"]
    L  = coef["L"]
    B0 = coef["B0"]
    B1 = coef["B1"]
    B2 = coef["B2"]
    B3 = coef["B3"]
    B4 = coef["B4"]
    B5 = coef["B5"]
    B6 = coef["B6"]

    exponent = B0 + B1 * kt + B2 * ast + B3 * z + B4 * delta_ktc
    k = C + L / (1.0 + _safe_exp(exponent)) + B5 * kde + B6 * k_extra
    return k


def _yang_type2(coef: dict, kt, ast, z, delta_ktc, kde, k_extra) -> float:
    """
    Yang2 / Yang4 / Yang5 公式结构（1-C 版本）：
        k = C + (1-C) / (1 + exp(B0 + B1*kt + B2*AST + B3*Z + B4*Δktc + B6*k_extra))
              + B5*kde
    """
    C  = coef["C"]
    B0 = coef["B0"]
    B1 = coef["B1"]
    B2 = coef["B2"]
    B3 = coef["B3"]
    B4 = coef["B4"]
    B5 = coef["B5"]
    B6 = coef["B6"]

    exponent = B0 + B1 * kt + B2 * ast + B3 * z + B4 * delta_ktc + B6 * k_extra
    k = C + (1.0 - C) / (1.0 + _safe_exp(exponent)) + B5 * kde
    return k


def run(inputs: dict) -> dict:
    """
    Yang 直散分离模型合并版（Yang1~Yang5）

    Yang1：引入卫星漫射分数 k_s，L 版公式
    Yang2：引入卫星漫射分数 k_s，(1-C) 版公式，k_s 进入指数项
    Yang3：用 k_hourly_engerer2 替代 k_s，L 版公式
    Yang4：用 k_hourly_engerer2 替代 k_s，(1-C) 版公式
    Yang5：Yang4 结构 + 按气候分区动态系数
    """

    # ── 读取公共输入 ──────────────────────────────────────────
    kt           = float(inputs["kt"])
    ast          = float(inputs["ast"])
    solar_zenith = float(inputs["solar_zenith"])
    ktc          = float(inputs["ktc"])
    ghi          = float(inputs["ghi"])
    ghc          = float(inputs["ghc"])
    model_type   = inputs.get("model_type", "yang4")
    k_s          = float(inputs.get("k_s", 0.0))
    k_hourly     = float(inputs.get("k_hourly_engerer2", 0.0))
    cluster      = str(inputs.get("cluster", "1"))

    # ── 公共计算 ──────────────────────────────────────────────
    delta_ktc = ktc - kt
    kde       = _compute_kde(ghi, ghc)

    # ── 按模型类型分支计算 ────────────────────────────────────
    if model_type == "yang1":
        k = _yang_type1(YANG1_COEF, kt, ast, solar_zenith, delta_ktc, kde, k_s)

    elif model_type == "yang2":
        k = _yang_type2(YANG2_COEF, kt, ast, solar_zenith, delta_ktc, kde, k_s)

    elif model_type == "yang3":
        k = _yang_type1(YANG3_COEF, kt, ast, solar_zenith, delta_ktc, kde, k_hourly)

    elif model_type == "yang4":
        k = _yang_type2(YANG4_COEF, kt, ast, solar_zenith, delta_ktc, kde, k_hourly)

    elif model_type == "yang5":
        if cluster not in YANG5_CLUSTER_COEF:
            raise ValueError(
                f"cluster 不合法：'{cluster}'，允许值为 1~5"
            )
        coef = YANG5_CLUSTER_COEF[cluster]
        k = _yang_type2(coef, kt, ast, solar_zenith, delta_ktc, kde, k_hourly)

    else:
        raise ValueError(
            f"model_type 不合法：'{model_type}'，"
            f"允许值为 yang1/yang2/yang3/yang4/yang5"
        )

    # ── 约束散射比到 [0, 1] ───────────────────────────────────
    k = max(0.0, min(1.0, k))

    # ── 派生输出 ──────────────────────────────────────────────
    dhi   = k * ghi
    cos_z = math.cos(math.radians(solar_zenith))
    bni   = (ghi - dhi) / cos_z if cos_z > 0.01 else 0.0

    dhi = max(0.0, dhi)
    bni = max(0.0, bni)

    return {
        "k":    round(k, 6),
        "dhi":  round(dhi, 4),
        "bni":  round(bni, 4),
        "k_de": round(kde, 6),
    }
