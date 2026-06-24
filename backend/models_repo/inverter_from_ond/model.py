# backend/models_repo/inverter_from_ond/model.py
"""
逆变器 OND 数据库驱动模型
使用 Sandia/Driesse 式61计算逆变器 AC 输出功率。
参数由路由层从逆变器数据库自动补全（p_aco/p_dco/p_so/c_o 均来自 OND 文件解析）。

Sandia 式61:
    当 Pdc <= Pso 时：Pac = 0
    当 Pdc > Pso 时：
        delta = Pdc - Pso
        denom = Pdco - Pso
        A     = Paco / denom - Co * denom
        Pac   = A * delta + Co * delta^2
        Pac   = clamp(Pac, 0, Paco)
"""


def run(inputs: dict) -> dict:
    p_dc  = float(inputs["p_dc"])
    p_aco = float(inputs["p_aco"])
    p_dco = float(inputs["p_dco"])
    p_so  = float(inputs["p_so"])
    c_o   = float(inputs["c_o"])

    # ── 输入校验 ──────────────────────────────────────────────
    if p_dc < 0:
        raise ValueError("p_dc 不能为负值")
    if p_aco <= 0:
        raise ValueError("p_aco（额定交流功率）必须大于 0，请检查逆变器数据库")
    if p_dco <= 0:
        raise ValueError("p_dco（额定直流功率）必须大于 0，请检查逆变器数据库")
    if p_dco <= p_so:
        raise ValueError(
            f"p_dco({p_dco}W) 须大于 p_so({p_so}W)，"
            "请检查逆变器数据库中的拟合参数或重新上传 OND 文件"
        )

    # ── Pdc 低于启动阈值：输出为零 ────────────────────────────
    if p_dc <= p_so:
        return {
            "p_ac":       0.0,
            "efficiency": 0.0,
            "p_loss":     round(p_dc, 4),
        }

    # ── Sandia 式61 ───────────────────────────────────────────
    denom  = p_dco - p_so
    delta  = p_dc  - p_so
    A      = p_aco / denom - c_o * denom
    p_ac   = A * delta + c_o * delta ** 2

    # 钳位至 [0, Paco]
    p_ac = max(0.0, min(p_ac, p_aco))

    efficiency = p_ac / p_dc if p_dc > 0 else 0.0
    p_loss     = p_dc - p_ac

    return {
        "p_ac":       round(p_ac,       4),
        "efficiency": round(efficiency, 6),
        "p_loss":     round(p_loss,     4),
    }
