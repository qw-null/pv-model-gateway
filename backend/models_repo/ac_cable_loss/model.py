def run(inputs: dict) -> dict:
    """
    交流电缆损失模型（模型40，式64~65）

    式64 — 电缆等效电阻：
        R_ac_wire = ρ × l / S

    式65 — 交流电缆损失功率：
        单相：P_ac_loss = 2 × Iac² × R_ac_wire   （去程+回程）
        三相：P_ac_loss = 3 × Iac² × R_ac_wire   （三相各一根）

    Parameters
    ----------
    rho          : 导体电阻率 (Ω·m)，铜默认 1.72e-8
    length       : 单根电缆长度 (m)
    cross_section: 电缆截面积 (m²)
    i_ac         : 交流线电流有效值 (A)
    phases       : 相数，1 或 3，默认 3
    """
    rho           = float(inputs.get("rho", 1.72e-8))
    length        = float(inputs["length"])
    cross_section = float(inputs["cross_section"])
    i_ac          = float(inputs["i_ac"])
    phases        = int(inputs.get("phases", 3))

    if length < 0:
        raise ValueError("length 不能为负值")
    if cross_section <= 0:
        raise ValueError("cross_section 须大于 0")
    if i_ac < 0:
        raise ValueError("i_ac 不能为负值")
    if phases not in (1, 3):
        raise ValueError("phases 须为 1 或 3")

    # ── 式64：电缆等效电阻 ────────────────────────────────────
    r_ac_wire = rho * length / cross_section

    # ── 式65：交流电缆损失 ────────────────────────────────────
    # 单相：2 根导线（去+回）；三相：3 根导线
    n_conductors = 2 if phases == 1 else 3
    p_ac_loss = n_conductors * i_ac ** 2 * r_ac_wire

    return {
        "r_ac_wire": round(r_ac_wire, 6),
        "p_ac_loss": round(p_ac_loss, 4)
    }
