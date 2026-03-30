def run(inputs: dict) -> dict:
    """
    线性电池温度模型（模型24~25）

    模型24 通用线性形式（式46）：
        Tcell = β0 + β1*Tamb + β2*Gc + β3*W

    模型25 NOCT 等价形式（式47）：
        Tcell = Tamb + (NOCT - 20) / 800 * Gc
        等价于：β0=0, β1=1, β2=(NOCT-20)/800, β3=0
    """
    tamb       = float(inputs["tamb"])
    gc         = float(inputs["gc"])
    wind_speed = float(inputs.get("wind_speed", 1.0))
    model_type = inputs.get("model_type", "noct")

    if model_type == "noct":
        noct   = float(inputs.get("noct", 45.0))
        t_cell = tamb + (noct - 20.0) / 800.0 * gc

    elif model_type == "general":
        beta0  = float(inputs.get("beta0", 0.0))
        beta1  = float(inputs.get("beta1", 1.0))
        beta2  = float(inputs.get("beta2", 0.03))
        beta3  = float(inputs.get("beta3", 0.0))
        t_cell = beta0 + beta1 * tamb + beta2 * gc + beta3 * wind_speed

    else:
        raise ValueError(
            f"model_type 不合法：'{model_type}'，允许值为 general / noct"
        )

    return {
        "t_cell": round(t_cell, 4)
    }
