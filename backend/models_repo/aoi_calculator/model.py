import math
def run(inputs: dict) -> dict:
    """
    计算直接辐射入射角（AOI）

    公式：
        cos(AOI) = sin(α)·cos(β) + cos(α)·cos(γs - γc)·sin(β)

    参数：
        alpha   : 太阳高度角 α（度）
        gamma_s : 太阳方位角 γs（度），正南为180°
        beta    : 组件倾斜角 β（度）
        gamma_c : 组件方位角 γc（度），正南为180°，正北为0°/360°  # ✅ 修改
    """
    alpha   = float(inputs["alpha"])
    gamma_s = float(inputs["gamma_s"])
    beta    = float(inputs["beta"])
    gamma_c = float(inputs["gamma_c"])

    # ── 参数范围校验 ────────────────────────────────────────────
    if not (-90.0 <= alpha <= 90.0):
        raise ValueError(f"太阳高度角 alpha 应在 [-90, 90] 范围内，当前值：{alpha}")
    if not (0.0 <= beta <= 180.0):
        raise ValueError(f"组件倾斜角 beta 应在 [0, 180] 范围内，当前值：{beta}")
    if not (0.0 <= gamma_c <= 360.0):                                        # ✅ 新增
        raise ValueError(f"组件方位角 gamma_c 应在 [0, 360] 范围内，当前值：{gamma_c}")

    # ── 角度转弧度 ─────────────────────────────────────────────
    alpha_rad   = math.radians(alpha)
    gamma_s_rad = math.radians(gamma_s)
    gamma_c_rad = math.radians(gamma_c)
    beta_rad    = math.radians(beta)

    # ── 核心公式计算 ────────────────────────────────────────────
    # cos(AOI) = sin(α)·cos(β) + cos(α)·cos(γs - γc)·sin(β)
    cos_aoi = (
        math.sin(alpha_rad) * math.cos(beta_rad)
        + math.cos(alpha_rad) * math.cos(gamma_s_rad - gamma_c_rad) * math.sin(beta_rad)
    )

    cos_aoi = max(-1.0, min(1.0, cos_aoi))
    aoi_deg = math.degrees(math.acos(cos_aoi))

    return {
        "AOI":     round(aoi_deg, 6),
        "cos_AOI": round(cos_aoi, 6),
    }
