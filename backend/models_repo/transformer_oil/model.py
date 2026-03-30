def run(inputs: dict) -> dict:
    """
    油浸式变压器损失模型（模型41，式66~67）

    铁损（式66）：
        P_Fe = β0 + β1 × P_trans_ref

    铜损（式67，含负载率修正）：
        P_Cu = β2 × P_trans_ref × k²

    其中 k 为负载率（0~1），满载时 k=1。

    适用范围：P_trans_ref ∈ [50, 2500] kVA，最高电压 ≤ 36 kV。

    Parameters
    ----------
    p_trans_ref : 额定变压器功率 (kVA)
    beta0       : 铁损截距系数 (kW)
    beta1       : 铁损斜率系数 (kW/kVA)
    beta2       : 铜损斜率系数 (kW/kVA)
    load_factor : 负载率 k，默认 1.0
    """
    p_trans_ref = float(inputs["p_trans_ref"])
    beta0       = float(inputs["beta0"])
    beta1       = float(inputs["beta1"])
    beta2       = float(inputs["beta2"])
    k           = float(inputs.get("load_factor", 1.0))

    if not (50.0 <= p_trans_ref <= 2500.0):
        raise ValueError("p_trans_ref 须在 50~2500 kVA 范围内（油浸式变压器）")
    if not (0.0 <= k <= 1.0):
        raise ValueError("load_factor 须在 0~1 范围内")

    # ── 式66：铁损 ────────────────────────────────────────────
    p_fe = beta0 + beta1 * p_trans_ref

    # ── 式67：铜损（含负载率） ────────────────────────────────
    p_cu = beta2 * p_trans_ref * k ** 2

    p_loss_total = p_fe + p_cu

    # 额定输出功率（kW）= 额定容量（kVA）× 功率因数（默认1）× 负载率
    p_out = p_trans_ref * k  # kVA → kW（功率因数取1）
    efficiency = p_out / (p_out + p_loss_total) if (p_out + p_loss_total) > 0 else 0.0

    return {
        "p_fe":          round(p_fe,          4),
        "p_cu":          round(p_cu,          4),
        "p_loss_total":  round(p_loss_total,  4),
        "efficiency":    round(efficiency,    6)
    }
