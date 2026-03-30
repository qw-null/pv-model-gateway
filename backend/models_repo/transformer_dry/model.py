def run(inputs: dict) -> dict:
    """
    干式变压器损失模型（模型42，式68~69）

    铁损（式68）：
        P_Fe = β0' + β1' × P_trans_ref

    铜损（式69，含负载率修正）：
        P_Cu = (β2' × P_trans_ref + β3' × P_trans_ref²) × k²

    与油浸式模型（模型41）的区别：
        铜损对 P_trans_ref 为二次方关系（而非线性）。

    适用范围：P_trans_ref ∈ [100, 3150] kVA，最高电压 ≤ 36 kV。

    Parameters
    ----------
    p_trans_ref  : 额定变压器功率 (kVA)
    beta0_prime  : 铁损截距系数 β0' (kW)
    beta1_prime  : 铁损斜率系数 β1' (kW/kVA)
    beta2_prime  : 铜损一次系数 β2' (kW/kVA)
    beta3_prime  : 铜损二次系数 β3' (kW/kVA²)
    load_factor  : 负载率 k，默认 1.0
    """
    p_trans_ref = float(inputs["p_trans_ref"])
    beta0_p     = float(inputs["beta0_prime"])
    beta1_p     = float(inputs["beta1_prime"])
    beta2_p     = float(inputs["beta2_prime"])
    beta3_p     = float(inputs["beta3_prime"])
    k           = float(inputs.get("load_factor", 1.0))

    if not (100.0 <= p_trans_ref <= 3150.0):
        raise ValueError("p_trans_ref 须在 100~3150 kVA 范围内（干式变压器）")
    if not (0.0 <= k <= 1.0):
        raise ValueError("load_factor 须在 0~1 范围内")

    # ── 式68：铁损 ────────────────────────────────────────────
    p_fe = beta0_p + beta1_p * p_trans_ref

    # ── 式69：铜损（二次方关系，含负载率） ───────────────────
    p_cu_rated = beta2_p * p_trans_ref + beta3_p * p_trans_ref ** 2
    p_cu       = p_cu_rated * k ** 2

    p_loss_total = p_fe + p_cu

    p_out = p_trans_ref * k
    efficiency = p_out / (p_out + p_loss_total) if (p_out + p_loss_total) > 0 else 0.0

    return {
        "p_fe":         round(p_fe,         4),
        "p_cu":         round(p_cu,         4),
        "p_loss_total": round(p_loss_total, 4),
        "efficiency":   round(efficiency,   6)
    }
