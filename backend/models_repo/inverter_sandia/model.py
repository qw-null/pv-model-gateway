def run(inputs: dict) -> dict:
    """
    Sandia 逆变器模型（模型37，式61）

        Pac = { (Paco / (Pdco - Pso)) - Co×(Pdco - Pso) } × (Pdc - Pso)
              + Co×(Pdc - Pso)²

    当 Pdc ≤ Pso 时，Pac = 0（低于启动阈值）。
    Pac 上限钳位至 Paco。

    Parameters
    ----------
    p_dc  : 直流输入功率 (W)
    p_aco : 额定交流功率 (W)
    p_dco : 额定直流功率 (W)
    p_so  : 启动自耗功率 (W)
    c_o   : 二次修正系数 (1/W)
    """
    p_dc  = float(inputs["p_dc"])
    p_aco = float(inputs["p_aco"])
    p_dco = float(inputs["p_dco"])
    p_so  = float(inputs["p_so"])
    c_o   = float(inputs["c_o"])

    if p_dc < 0:
        raise ValueError("p_dc 不能为负值")
    if p_dco <= p_so:
        raise ValueError("p_dco 须大于 p_so")

    # ── 式61 ──────────────────────────────────────────────────
    if p_dc <= p_so:
        p_ac = 0.0
    else:
        denom  = p_dco - p_so
        linear = p_aco / denom - c_o * denom
        delta  = p_dc - p_so

        p_ac = linear * delta + c_o * delta ** 2
        p_ac = max(0.0, min(p_ac, p_aco))

    efficiency = p_ac / p_dc if p_dc > 0 else 0.0
    p_loss     = p_dc - p_ac

    return {
        "p_ac":       round(p_ac,       4),
        "efficiency": round(efficiency, 6),
        "p_loss":     round(p_loss,     4)
    }
