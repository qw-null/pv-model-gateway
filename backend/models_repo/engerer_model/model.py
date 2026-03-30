import math


# ══════════════════════════════════════════════════════════════
# 三种 Engerer 模型系数表
# ══════════════════════════════════════════════════════════════

COEFFICIENTS = {
    "engerer1": {
        "C":  0.1527,
        "B0": -4.1092,
        "B1":  6.1661,
        "B2": -2.2304e-3,
        "B3":  1.1026e-2,
        "B4": -4.3314,
        "B5":  None,          # Engerer1 无 B5
    },
    "engerer2": {
        "C":  4.2336e-2,
        "B0": -3.7912,
        "B1":  7.5479,
        "B2": -1.0036e-2,
        "B3":  3.1480e-3,
        "B4": -5.3146,
        "B5":  1.7073,        # 云增强线性校正系数
    },
    "engerer3": {
        "C":  0.1090,
        "B0": -2.0506e-2,
        "B1":  8.1249,
        "B2": -3.6234e-2,
        "B3": -4.1397e-2,
        "B4": -5.1045,
        "B5":  None,          # Engerer3 无 B5
    },
}


def run(inputs: dict) -> dict:
    """
    Engerer 直散分离模型（合并版，支持 engerer1 / engerer2 / engerer3）

    Engerer1 / Engerer3 公式：
        k = C + (1 - C) / (1 + exp(B0 + B1*kt + B2*AST + B3*Z + B4*Δktc))

    Engerer2 公式（增加云增强线性校正项）：
        kde = max(0, 1 - Ghc / Ghi)
        k   = C + (1 - C) / (1 + exp(B0 + B1*kt + B2*AST + B3*Z + B4*Δktc)) + B5 * kde

    其中：
        Δktc = ktc - kt
        BNI  = (GHI - DHI) / cos(Z)
    """

    # ── 读取输入 ──────────────────────────────────────────────
    kt          = float(inputs["kt"])
    ast         = float(inputs["ast"])
    solar_zenith = float(inputs["solar_zenith"])
    ktc         = float(inputs["ktc"])
    ghi         = float(inputs["ghi"])
    ghc         = float(inputs["ghc"])
    model_type  = inputs.get("model_type", "engerer2")

    # ── 校验模型类型 ──────────────────────────────────────────
    if model_type not in COEFFICIENTS:
        raise ValueError(
            f"model_type 不合法：'{model_type}'，"
            f"允许值为 {list(COEFFICIENTS.keys())}"
        )

    coef = COEFFICIENTS[model_type]
    C  = coef["C"]
    B0 = coef["B0"]
    B1 = coef["B1"]
    B2 = coef["B2"]
    B3 = coef["B3"]
    B4 = coef["B4"]
    B5 = coef["B5"]

    # ── 核心计算 ──────────────────────────────────────────────

    # 偏差项 Δktc = ktc - kt
    delta_ktc = ktc - kt

    # Logistic 指数项
    exponent = B0 + B1 * kt + B2 * ast + B3 * solar_zenith + B4 * delta_ktc

    # 防止指数溢出
    exponent = max(-500.0, min(500.0, exponent))

    # S 型函数基础散射比
    k = C + (1.0 - C) / (1.0 + math.exp(exponent))

    # 云增强修正（仅 Engerer2）
    k_de = 0.0
    if model_type == "engerer2" and B5 is not None:
        k_de = max(0.0, 1.0 - ghc / ghi) if ghi > 0 else 0.0
        k += B5 * k_de

    # 约束散射比到 [0, 1]
    k = max(0.0, min(1.0, k))

    # ── 派生输出 ──────────────────────────────────────────────

    # 漫射水平辐照度 DHI
    dhi = k * ghi

    # 光束法向辐照度 BNI = (GHI - DHI) / cos(Z)
    cos_z = math.cos(math.radians(solar_zenith))
    if cos_z > 0.01:
        bni = (ghi - dhi) / cos_z
    else:
        bni = 0.0

    # 确保非负
    dhi = max(0.0, dhi)
    bni = max(0.0, bni)

    return {
        "k":    round(k, 6),
        "dhi":  round(dhi, 4),
        "bni":  round(bni, 4),
        "k_de": round(k_de, 6),
    }
