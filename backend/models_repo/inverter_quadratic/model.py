def run(inputs: dict) -> dict:
    """
    逆变器二次函数损失模型（模型35，式59）

        Ploss = a0 + a1×Pout + a2×Pout²

    其中：
        a0 — 固定自耗（控制/驱动电路）
        a1 — 线性损耗（半导体固定压降）
        a2 — 欧姆损耗（导线、开关导通电阻）

    Parameters
    ----------
    p_out : 交流输出功率 (W)
    a0    : 固定损耗系数 (W)
    a1    : 线性损耗系数 (无量纲)
    a2    : 二次损耗系数 (1/W)
    """
    p_out = float(inputs["p_out"])
    a0    = float(inputs["a0"])
    a1    = float(inputs["a1"])
    a2    = float(inputs["a2"])

    if p_out < 0:
        raise ValueError("p_out 不能为负值")

    # ── 式59 ──────────────────────────────────────────────────
    p_loss = a0 + a1 * p_out + a2 * p_out ** 2

    p_in       = p_out + p_loss
    efficiency = p_out / p_in if p_in > 0 else 0.0

    return {
        "p_loss":     round(p_loss,     4),
        "p_in":       round(p_in,       4),
        "efficiency": round(efficiency, 6)
    }
