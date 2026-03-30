def run(inputs: dict) -> dict:
    """
    King 逆变器效率模型（模型34，式59~62）

    交流输出功率：
        Pac = (Pac_ref / (A - B)) - C×(A - B)  ×  (Pdc - B) + C×(Pdc - B)²

    辅助量（式60~62）：
        A = Pdc_ref × [1 + C1×(Vdc - Vdc_ref)]
        B = Ps_ref  × [1 + C2×(Vdc - Vdc_ref)]
        C = C0      × [1 + C3×(Vdc - Vdc_ref)]

    当 Pdc ≤ B（输入功率低于启动阈值）时，Pac = 0。
    Pac 上限钳位至 Pac_ref。

    Parameters
    ----------
    p_dc     : 直流输入功率 (W)
    v_dc     : 直流输入电压 (V)
    p_ac_ref : 额定交流功率 (W)
    p_dc_ref : 额定直流功率 (W)
    v_dc_ref : 额定直流电压 (V)
    p_s_ref  : 启动功率阈值 (W)
    c0~c3    : 经验系数
    """
    p_dc     = float(inputs["p_dc"])
    v_dc     = float(inputs["v_dc"])
    p_ac_ref = float(inputs["p_ac_ref"])
    p_dc_ref = float(inputs["p_dc_ref"])
    v_dc_ref = float(inputs["v_dc_ref"])
    p_s_ref  = float(inputs["p_s_ref"])
    c0       = float(inputs["c0"])
    c1       = float(inputs["c1"])
    c2       = float(inputs["c2"])
    c3       = float(inputs["c3"])

    # ── 输入校验 ──────────────────────────────────────────────
    if p_dc < 0:
        raise ValueError("p_dc 不能为负值")
    if v_dc <= 0:
        raise ValueError("v_dc 须大于 0")

    # ── 式60~62：辅助量 A、B、C ───────────────────────────────
    dv = v_dc - v_dc_ref
    A = p_dc_ref * (1.0 + c1 * dv)   # 式(60)
    B = p_s_ref  * (1.0 + c2 * dv)   # 式(61)
    C = c0       * (1.0 + c3 * dv)   # 式(62)

    # ── 式59：交流输出功率 ────────────────────────────────────
    # 低于启动阈值时无输出
    if p_dc <= B:
        p_ac = 0.0
    else:
        denom = A - B
        if abs(denom) < 1e-12:
            p_ac = 0.0
        else:
            p_ac = (
                (p_ac_ref / denom - C * denom) * (p_dc - B)
                + C * (p_dc - B) ** 2
            )
        # 钳位：不超过额定值，不低于 0
        p_ac = max(0.0, min(p_ac, p_ac_ref))

    # ── 效率与损耗 ────────────────────────────────────────────
    efficiency = p_ac / p_dc if p_dc > 0 else 0.0
    p_loss     = p_dc - p_ac

    return {
        "p_ac":       round(p_ac,       4),
        "efficiency": round(efficiency, 6),
        "p_loss":     round(p_loss,     4)
    }
