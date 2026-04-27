# backend/core/iv_curve.py
"""
基于单二极管模型（SDM）计算光伏组件 IV / PV 曲线
支持两种扫描模式：
  - 辐照度模式：固定温度，扫描多个辐照度
  - 温度模式：固定辐照度，扫描多个温度
"""
import math


def _calc_iv_curve(
    isc:       float,
    voc:       float,
    imp:       float,
    vmp:       float,
    r_series:  float,
    r_shunt:   float,
    gamma:     float,
    mu_isc:    float,
    mu_voc:    float,
    g_ref:     float,
    t_ref:     float,
    g:         float,
    t:         float,
    n_cells:   int = 54,
    n_points:  int = 200,
) -> dict:
    delta_t = t - t_ref
    g_ratio = g / g_ref if g_ref > 0 else 1.0

    isc_op = isc * g_ratio * (1 + mu_isc / 1000 * delta_t)
    voc_op = voc + mu_voc / 1000 * delta_t + (
        gamma * 26e-3 * math.log(g_ratio) if g_ratio > 0 else 0
    )
    voc_op = max(voc_op, 0.1)

    T_k = t + 273.15
    Vt  = gamma * n_cells * 1.381e-23 * T_k / 1.602e-19

    i0 = isc_op / (math.exp(voc_op / Vt) - 1) if Vt > 0 else 1e-10
    i0 = max(i0, 1e-15)

    voltages, currents = [], []
    v_step = voc_op / (n_points - 1)

    for i_v in range(n_points):
        v = i_v * v_step
        i_guess = max(0.0, min(
            isc_op - i0 * (math.exp((v + isc_op * r_series) / Vt) - 1),
            isc_op
        ))
        for _ in range(50):
            exp_term = math.exp(min((v + i_guess * r_series) / Vt, 300))
            f  = isc_op - i0 * (exp_term - 1) - (v + i_guess * r_series) / r_shunt - i_guess
            df = -i0 * r_series / Vt * exp_term - r_series / r_shunt - 1
            if abs(df) < 1e-15:
                break
            delta = f / df
            i_guess = max(0.0, i_guess - delta)
            if abs(delta) < 1e-9:
                break
        voltages.append(round(v, 4))
        currents.append(round(max(i_guess, 0.0), 6))

    powers  = [round(v * i, 4) for v, i in zip(voltages, currents)]
    pmp_idx = powers.index(max(powers))

    return {
        "voltages": voltages,
        "currents": currents,
        "powers":   powers,
        "voc":      round(voc_op, 4),
        "isc":      round(isc_op, 4),
        "vmp":      round(voltages[pmp_idx], 4),
        "imp":      round(currents[pmp_idx], 4),
        "pmp":      round(powers[pmp_idx],   4),
    }


def calc_curves_by_irradiance(panel_params: dict, irradiances: list, base_temp: float) -> list:
    """辐照度模式：固定温度，扫描多个辐照度"""
    results = []
    for g in irradiances:
        curve = _calc_iv_curve(g=g, t=base_temp, **_extract(panel_params))
        curve["irradiance"] = g
        curve["temperature"] = base_temp
        results.append(curve)
    return results


def calc_curves_by_temperature(panel_params: dict, temperatures: list, base_irradiance: float) -> list:
    """温度模式：固定辐照度，扫描多个温度"""
    results = []
    for t in temperatures:
        curve = _calc_iv_curve(g=base_irradiance, t=t, **_extract(panel_params))
        curve["irradiance"]  = base_irradiance
        curve["temperature"] = t
        results.append(curve)
    return results


def _extract(p: dict) -> dict:
    return dict(
        isc      = p["isc"],
        voc      = p["voc"],
        imp      = p["imp"],
        vmp      = p["vmp"],
        r_series = p.get("r_series",    0.037),
        r_shunt  = p.get("r_shunt",     1000.0),
        gamma    = p.get("gamma",       1.255),
        mu_isc   = p.get("temp_coeff",  6.22),
        mu_voc   = p.get("mu_voc_spec", -92.5),
        g_ref    = p.get("g_ref",       1000.0),
        t_ref    = p.get("t_ref",       25.0),
    )
