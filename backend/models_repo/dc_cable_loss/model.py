def run(inputs: dict) -> dict:
    """
    直流电缆损失模型（模型39，式63）

    直流欧姆损失率：
        L_dc = (Ns × Np × R_dc_wire × Impp²) / Pmpp

    其中：
        Pmpp = Ns × Np × Vmpp × Impp   （阵列总 MPP 功率）

    直流损失功率：
        P_dc_loss = L_dc × Pmpp
                  = Ns × Np × R_dc_wire × Impp²

    Parameters
    ----------
    ns         : 串联组件数
    np         : 并联组串数
    r_dc_wire  : 直流电缆等效电阻 (Ω)
    i_mpp      : MPP 电流 (A)
    v_mpp      : MPP 电压 (V)
    """
    ns        = int(inputs["ns"])
    np_       = int(inputs["np"])
    r_dc_wire = float(inputs["r_dc_wire"])
    i_mpp     = float(inputs["i_mpp"])
    v_mpp     = float(inputs["v_mpp"])

    if ns < 1 or np_ < 1:
        raise ValueError("ns 和 np 须为正整数")
    if r_dc_wire < 0:
        raise ValueError("r_dc_wire 不能为负值")
    if i_mpp < 0 or v_mpp < 0:
        raise ValueError("i_mpp 和 v_mpp 不能为负值")

    # ── 阵列 MPP 总功率 ───────────────────────────────────────
    p_mpp = ns * np_ * v_mpp * i_mpp

    # ── 式63：直流欧姆损失 ────────────────────────────────────
    # P_dc_loss = Ns × Np × R_dc_wire × Impp²
    p_dc_loss = ns * np_ * r_dc_wire * i_mpp ** 2

    loss_ratio = p_dc_loss / p_mpp if p_mpp > 0 else 0.0
    p_dc_out   = max(0.0, p_mpp - p_dc_loss)

    return {
        "p_mpp":      round(p_mpp,      4),
        "p_dc_loss":  round(p_dc_loss,  4),
        "loss_ratio": round(loss_ratio, 6),
        "p_dc_out":   round(p_dc_out,   4)
    }
