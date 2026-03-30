def run(inputs: dict) -> dict:
    """
    线性电压依赖二次损失模型（模型38，式62）

    使用归一化量（pin、vin），系数随 (vin - 1) 线性变化：

        ploss = (b00 + b01×(vin-1))
              + (b10 + b11×(vin-1))×pin
              + (b20 + b21×(vin-1))×pin²

    本质是双二次模型（模型36）去掉 Vin² 项后的简化形式。

    Parameters
    ----------
    p_in  : 归一化直流输入功率 pin（Pdc/Prated）
    v_in  : 归一化直流输入电压 vin（Vdc/Vrated）
    b00   : b0 常数项
    b01   : b0 线性项系数
    b10   : b1 常数项
    b11   : b1 线性项系数
    b20   : b2 常数项
    b21   : b2 线性项系数
    """
    p_in = float(inputs["p_in"])
    v_in = float(inputs["v_in"])

    b00 = float(inputs["b00"])
    b01 = float(inputs["b01"])
    b10 = float(inputs["b10"])
    b11 = float(inputs["b11"])
    b20 = float(inputs["b20"])
    b21 = float(inputs["b21"])

    if p_in < 0:
        raise ValueError("p_in 不能为负值")
    if v_in < 0:
        raise ValueError("v_in 不能为负值")

    # ── 式62：线性电压依赖系数 ────────────────────────────────
    dv = v_in - 1.0

    b0 = b00 + b01 * dv
    b1 = b10 + b11 * dv
    b2 = b20 + b21 * dv

    # ── 归一化损耗 ────────────────────────────────────────────
    p_loss = b0 + b1 * p_in + b2 * p_in ** 2

    p_out      = max(0.0, p_in - p_loss)
    efficiency = p_out / p_in if p_in > 0 else 0.0

    return {
        "p_loss":     round(p_loss,     6),
        "p_out":      round(p_out,      6),
        "efficiency": round(efficiency, 6)
    }
