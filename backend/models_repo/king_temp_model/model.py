import math


def run(inputs: dict) -> dict:
    """
    King 非线性电池温度模型（模型26~27）

    式(49) 组件温度：
        Tmod = Gc * exp(a + b*W) + Tamb

    式(48) 电池温度：
        Tcell = Tmod + Gc / 1000 * ΔT
    """
    tamb       = float(inputs["tamb"])
    gc         = float(inputs["gc"])
    wind_speed = float(inputs["wind_speed"])
    a          = float(inputs.get("a",       -3.56))
    b          = float(inputs.get("b",       -0.075))
    delta_t    = float(inputs.get("delta_t",  3.0))

    # ── 组件温度（式49）──────────────────────────────────────
    t_mod = gc * math.exp(a + b * wind_speed) + tamb

    # ── 电池温度（式48）──────────────────────────────────────
    t_cell = t_mod + (gc / 1000.0) * delta_t

    return {
        "t_cell": round(t_cell, 4),
        "t_mod":  round(t_mod,  4),
    }
