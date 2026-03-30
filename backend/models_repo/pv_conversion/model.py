def run(inputs: dict) -> dict:
    import pvlib

    poa       = inputs["poa_irradiance"]
    temp      = inputs["cell_temp"]
    pdc0      = inputs.get("pdc0", 250.0)
    gamma_pdc = inputs.get("gamma_pdc", -0.004)

    # 使用 pvlib PVWatts 直流模型
    p_dc = pvlib.pvsystem.pvwatts_dc(poa, temp, pdc0, gamma_pdc)
    p_dc = float(p_dc)

    # 简化估算 I_mp, V_mp（假设标准组件参数）
    v_mp = 30.0 * (1 + gamma_pdc * (temp - 25))
    i_mp = p_dc / v_mp if v_mp > 0 else 0.0

    # 效率 = 实际功率 / (辐照度 * 组件面积)，此处以额定效率近似
    efficiency = (p_dc / pdc0 * 100) if pdc0 > 0 else 0.0

    return {
        "p_dc":       round(p_dc, 4),
        "efficiency": round(efficiency, 2),
        "i_mp":       round(i_mp, 4),
        "v_mp":       round(v_mp, 4),
    }
