def run(inputs: dict) -> dict:
    """
    逆变器双二次损失模型（模型36，式60）

    系数随输入电压变化（式60）：
        ai = ai0 + ai1×Vin + ai2×Vin²   (i = 0, 1, 2)

    损耗（式59 结构）：
        Ploss = a0 + a1×Pout + a2×Pout²

    Parameters
    ----------
    p_out       : 交流输出功率 (W)
    v_in        : 直流输入电压 (V)
    a00~a02     : a0 的多项式系数
    a10~a12     : a1 的多项式系数
    a20~a22     : a2 的多项式系数
    """
    p_out = float(inputs["p_out"])
    v_in  = float(inputs["v_in"])

    a00 = float(inputs["a00"])
    a01 = float(inputs["a01"])
    a02 = float(inputs["a02"])

    a10 = float(inputs["a10"])
    a11 = float(inputs["a11"])
    a12 = float(inputs["a12"])

    a20 = float(inputs["a20"])
    a21 = float(inputs["a21"])
    a22 = float(inputs["a22"])

    if p_out < 0:
        raise ValueError("p_out 不能为负值")
    if v_in < 0:
        raise ValueError("v_in 不能为负值")

    # ── 式60：计算电压依赖系数 ────────────────────────────────
    a0 = a00 + a01 * v_in + a02 * v_in ** 2
    a1 = a10 + a11 * v_in + a12 * v_in ** 2
    a2 = a20 + a21 * v_in + a22 * v_in ** 2

    # ── 损耗（式59 结构）──────────────────────────────────────
    p_loss = a0 + a1 * p_out + a2 * p_out ** 2

    p_in       = p_out + p_loss
    efficiency = p_out / p_in if p_in > 0 else 0.0

    return {
        "p_loss":     round(p_loss,     4),
        "p_in":       round(p_in,       4),
        "efficiency": round(efficiency, 6)
    }
