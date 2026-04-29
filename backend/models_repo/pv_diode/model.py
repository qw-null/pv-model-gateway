import math

K_BOLTZMANN = 1.380649e-23
Q_ELECTRON = 1.602176634e-19
EG_SILICON = 1.12
T_REF_K = 298.15

def _thermal_voltage(t_cell_c, n, ns):
    tc_k = t_cell_c + 273.15
    return ns * n * K_BOLTZMANN * tc_k / Q_ELECTRON

def _adjust_il(gc, t_cell_c, il_ref, alpha_isc=0.0005):
    return il_ref * (gc / 1000.0) * (1.0 + alpha_isc * (t_cell_c - 25.0))

def _adjust_io(t_cell_c, io_ref):
    tc_k = t_cell_c + 273.15
    ratio = tc_k / T_REF_K
    exp_arg = (EG_SILICON * Q_ELECTRON / K_BOLTZMANN) * (1.0 / T_REF_K - 1.0 / tc_k)
    return io_ref * (ratio ** 3) * math.exp(exp_arg)

def _adjust_rsh(gc, rsh_ref):
    return rsh_ref * (1000.0 / max(gc, 1.0))

def _solve_current(v, il, io, rs, rsh, a, max_iter=60, tol=1e-9):
    i = il
    for _ in range(max_iter):
        v_j = v + rs * i
        exp_k = math.exp(min(v_j / a, 500.0))
        f = il - io * (exp_k - 1.0) - v_j / rsh - i
        df = -io * exp_k * rs / a - rs / rsh - 1.0
        if abs(df) < 1e-15:
            break
        delta = f / df
        i = max(i - delta, 0.0)
        if abs(delta) < tol:
            break
    return i

def _compute_iv_curve(il, io, rs, rsh, a, n_points=200):
    voc_est = a * math.log(il / io + 1.0)
    iv = []
    for k in range(n_points + 1):
        v = voc_est * k / n_points
        current = _solve_current(v, il, io, rs, rsh, a)
        iv.append({"voltage": round(v, 6), "current": round(current, 6), "power": round(v * current, 6)})
    return iv

def _extract_key_points(iv):
    if not iv:
        return {}
    isc = iv[0]["current"]
    voc = iv[-1]["voltage"]
    best = max(iv, key=lambda pt: pt["power"])
    pmpp = best["power"]
    ff = pmpp / (voc * isc) if voc * isc > 0 else 0.0
    return {"voc": round(voc, 6), "isc": round(isc, 6),
            "vmpp": round(best["voltage"], 6), "impp": round(best["current"], 6),
            "pmpp": round(pmpp, 6), "ff": round(ff, 6)}

def run(inputs: dict) -> dict:
    # 参数已由路由层从组件库补全，直接读取
    gc      = float(inputs["g_poa"])
    t_cell  = float(inputs["t_cell"])
    isc_ref = float(inputs["isc"])
    voc_ref = float(inputs["voc"])
    imp_ref = float(inputs["imp"])
    vmp_ref = float(inputs["vmp"])
    ns      = int(inputs.get("ns", 60))
    rs      = float(inputs.get("r_series", 0.5))
    rsh_ref = float(inputs.get("r_shunt", 200.0))
    n       = float(inputs.get("gamma", 1.2))

    # 由 isc/voc/imp/vmp 估算 il_ref 和 io_ref（STC下）
    il_ref = isc_ref
    a_ref  = _thermal_voltage(25.0, n, ns)
    io_ref = (isc_ref - vmp_ref / rsh_ref) / (math.exp(voc_ref / a_ref) - 1)
    io_ref = max(io_ref, 1e-12)

    il  = _adjust_il(gc, t_cell, il_ref)
    io  = _adjust_io(t_cell, io_ref)
    rsh = _adjust_rsh(gc, rsh_ref)
    a   = _thermal_voltage(t_cell, n, ns)

    if gc == 0:
        return {"current": 0.0, "power": 0.0, "voc": 0.0, "isc": 0.0,
                "vmpp": 0.0, "impp": 0.0, "pmpp": 0.0, "ff": 0.0}

    iv = _compute_iv_curve(il, io, rs, rsh, a)
    kp = _extract_key_points(iv)
    # 返回 MPP 工作点电流/功率作为主输出
    return {
        "current": kp.get("impp", 0.0),
        "power":   kp.get("pmpp", 0.0),
        **kp,
    }
