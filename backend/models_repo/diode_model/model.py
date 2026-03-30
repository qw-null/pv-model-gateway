import math

# ══════════════════════════════════════════════════════════════
# 物理常数
# ══════════════════════════════════════════════════════════════
K_BOLTZMANN = 1.380649e-23    # 玻尔兹曼常数 (J/K)
Q_ELECTRON  = 1.602176634e-19 # 电子电荷 (C)
EG_SILICON  = 1.12            # 硅带隙 (eV)
T_REF_K     = 298.15          # STC参考温度 (K)，25°C
G_REF       = 1000.0          # STC参考辐照度 (W/m²)


# ══════════════════════════════════════════════════════════════
# 参数调整
# ══════════════════════════════════════════════════════════════

def _thermal_voltage(t_cell_c: float, n: float, ns: int) -> float:
    """
    修正热电压（式57）：a = Ns × n × k × Tc / q

    Parameters
    ----------
    t_cell_c : 电池温度 (°C)
    n        : 理想因子
    ns       : 串联电池数
    """
    tc_k = t_cell_c + 273.15
    return ns * n * K_BOLTZMANN * tc_k / Q_ELECTRON


def _adjust_il(gc: float, t_cell_c: float, il_ref: float,
               alpha_isc: float = 0.0005) -> float:
    """
    光电流温度/辐照度修正：
        IL = IL_ref × (Gc / G_ref) × [1 + α_Isc × (Tc - 25)]
    """
    return il_ref * (gc / G_REF) * (1.0 + alpha_isc * (t_cell_c - 25.0))


def _adjust_io(t_cell_c: float, io_ref: float) -> float:
    """
    反向饱和电流温度修正（含带隙项）：
        I0 = I0_ref × (Tc/Tref)³ × exp[Eg/k × (1/Tref - 1/Tc)]
    """
    tc_k = t_cell_c + 273.15
    ratio = tc_k / T_REF_K
    exp_arg = (EG_SILICON * Q_ELECTRON / K_BOLTZMANN) * (1.0 / T_REF_K - 1.0 / tc_k)
    return io_ref * (ratio ** 3) * math.exp(exp_arg)


def _adjust_rsh(gc: float, rsh_ref: float) -> float:
    """
    并联电阻辐照度修正：Rsh = Rsh_ref × (G_ref / Gc)
    """
    return rsh_ref * (G_REF / max(gc, 1.0))


# ══════════════════════════════════════════════════════════════
# 牛顿-拉夫逊隐式求解核心
# ══════════════════════════════════════════════════════════════

def _solve_current(v: float, il: float, io_list: list,
                   rs: float, rsh: float, a_list: list,
                   max_iter: int = 60, tol: float = 1e-9) -> float:
    """
    统一隐式求解：对任意数量的二极管，牛顿-拉夫逊迭代求 I

    方程（式56 / 式58 统一形式）：
        F(I) = IL - Σ I0i×[exp((V+Rs×I)/ai) - 1] - (V+Rs×I)/Rsh - I = 0

    Parameters
    ----------
    v       : 端电压 (V)
    il      : 光电流 (A)
    io_list : 各二极管饱和电流列表 [I01, I02, ...]
    rs      : 串联电阻 (Ω)
    rsh     : 并联电阻 (Ω)
    a_list  : 各二极管修正热电压列表 [a1, a2, ...]
    """
    i = il  # 初始猜测：开路附近

    for _ in range(max_iter):
        v_j = v + rs * i  # 结电压

        f  = il - v_j / rsh - i
        df = -rs / rsh - 1.0

        for io_k, a_k in zip(io_list, a_list):
            arg = v_j / a_k
            # 防止指数溢出
            exp_k = math.exp(min(arg, 500.0))
            f  -= io_k * (exp_k - 1.0)
            df -= io_k * exp_k * rs / a_k

        if abs(df) < 1e-15:
            break

        delta = f / df
        i_new = i - delta

        # 电流不允许为负
        i = max(i_new, 0.0)

        if abs(delta) < tol:
            break

    return i


# ══════════════════════════════════════════════════════════════
# I-V 曲线计算
# ══════════════════════════════════════════════════════════════

def _compute_iv_curve(il: float, io_list: list, rs: float,
                      rsh: float, a_list: list,
                      n_points: int = 200) -> list:
    """
    扫描 0 → Voc 计算完整 I-V 曲线

    Voc 初始估算：a1 × ln(IL/I01 + 1)
    """
    voc_est = a_list[0] * math.log(il / io_list[0] + 1.0)

    iv = []
    for k in range(n_points + 1):
        v = voc_est * k / n_points
        current = _solve_current(v, il, io_list, rs, rsh, a_list)
        iv.append({
            "voltage": round(v, 6),
            "current": round(current, 6),
            "power":   round(v * current, 6)
        })

    return iv


def _extract_key_points(iv: list) -> dict:
    """
    从 I-V 曲线提取 Isc、Voc、MPP、FF
    """
    if not iv:
        return {}

    isc = iv[0]["current"]
    voc = iv[-1]["voltage"]

    best = max(iv, key=lambda pt: pt["power"])
    vmpp = best["voltage"]
    impp = best["current"]
    pmpp = best["power"]

    ff = pmpp / (voc * isc) if voc * isc > 0 else 0.0

    return {
        "voc":  round(voc,  6),
        "isc":  round(isc,  6),
        "vmpp": round(vmpp, 6),
        "impp": round(impp, 6),
        "pmpp": round(pmpp, 6),
        "ff":   round(ff,   6)
    }


# ══════════════════════════════════════════════════════════════
# 主入口
# ══════════════════════════════════════════════════════════════

def run(inputs: dict) -> dict:
    """
    光伏组件二极管模型（模型31~33）

    模型31 — 单二极管（式56、57）：
        I = IL - I0×[exp((V+Rs×I)/a) - 1] - (V+Rs×I)/Rsh
        a = Ns×n1×k×Tc/q

    模型32 — 双二极管（式58，m=2）：
        I = IL - I01×[exp((V+Rs×I)/a1)-1]
               - I02×[exp((V+Rs×I)/a2)-1]
               - (V+Rs×I)/Rsh

    模型33 — 三二极管（式58，m=3）：
        I = IL - Σ_{i=1}^{3} I0i×[exp((V+Rs×I)/ai)-1]
               - (V+Rs×I)/Rsh

    Inputs
    ------
    gc         : 有效辐照度 (W/m²)，必填
    t_cell     : 电池温度 (°C)，必填
    voltage    : 工作电压 (V)，可选；不填则输出完整I-V曲线
    model_type : "single" | "double" | "triple"，默认 "single"
    il_ref     : STC光电流 (A)，默认 5.0
    io_ref     : STC第一饱和电流 (A)，默认 1e-9
    rs         : 串联电阻 (Ω)，默认 0.5
    rsh_ref    : STC并联电阻 (Ω)，默认 200.0
    n          : 第一理想因子，默认 1.2
    ns         : 串联电池数，默认 60
    io2_ref    : STC第二饱和电流 (A)，double/triple用，默认 1e-7
    n2         : 第二理想因子，double/triple用，默认 2.0
    io3_ref    : STC第三饱和电流 (A)，triple用，默认 1e-6
    n3         : 第三理想因子，triple用，默认 3.0

    Outputs（单点）
    ---------------
    current : 输出电流 (A)
    power   : 输出功率 (W)

    Outputs（完整曲线）
    -------------------
    iv_curve : [{voltage, current, power}, ...]
    voc, isc, vmpp, impp, pmpp, ff
    """
    # ── 读取输入 ──────────────────────────────────────────────
    gc         = float(inputs["gc"])
    t_cell     = float(inputs["t_cell"])
    voltage    = inputs.get("voltage")
    model_type = inputs.get("model_type", "single")

    il_ref  = float(inputs.get("il_ref",   5.0))
    io_ref  = float(inputs.get("io_ref",   1e-9))
    rs      = float(inputs.get("rs",       0.5))
    rsh_ref = float(inputs.get("rsh_ref",  200.0))
    n1      = float(inputs.get("n",        1.2))
    ns      = int(inputs.get("ns",         60))

    io2_ref = float(inputs.get("io2_ref",  1e-7))
    n2      = float(inputs.get("n2",       2.0))
    io3_ref = float(inputs.get("io3_ref",  1e-6))
    n3      = float(inputs.get("n3",       3.0))

    # ── 输入校验 ──────────────────────────────────────────────
    if gc < 0:
        raise ValueError("gc 不能为负值")
    if gc == 0:
        # 无光照，直接返回零
        if voltage is not None:
            return {"current": 0.0, "power": 0.0}
        return {"iv_curve": [], "voc": 0.0, "isc": 0.0,
                "vmpp": 0.0, "impp": 0.0, "pmpp": 0.0, "ff": 0.0}

    valid_types = {"single", "double", "triple"}
    if model_type not in valid_types:
        raise ValueError(f"model_type 须为 {valid_types}，实际传入：'{model_type}'")

    # ── 参数修正 ──────────────────────────────────────────────
    il  = _adjust_il(gc, t_cell, il_ref)
    io1 = _adjust_io(t_cell, io_ref)
    io2 = _adjust_io(t_cell, io2_ref)
    io3 = _adjust_io(t_cell, io3_ref)
    rsh = _adjust_rsh(gc, rsh_ref)

    a1 = _thermal_voltage(t_cell, n1, ns)
    a2 = _thermal_voltage(t_cell, n2, ns)
    a3 = _thermal_voltage(t_cell, n3, ns)

    # ── 按模型类型组装参数列表 ────────────────────────────────
    if model_type == "single":
        io_list = [io1]
        a_list  = [a1]
    elif model_type == "double":
        io_list = [io1, io2]
        a_list  = [a1,  a2]
    else:  # triple
        io_list = [io1, io2, io3]
        a_list  = [a1,  a2,  a3]

    # ── 单点 or 完整曲线 ──────────────────────────────────────
    if voltage is not None:
        v = float(voltage)
        if v < 0:
            raise ValueError("voltage 不能为负值")
        current = _solve_current(v, il, io_list, rs, rsh, a_list)
        return {
            "current": round(current, 6),
            "power":   round(v * current, 6)
        }
    else:
        iv = _compute_iv_curve(il, io_list, rs, rsh, a_list)
        return {"iv_curve": iv, **_extract_key_points(iv)}
