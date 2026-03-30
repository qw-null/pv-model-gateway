MODEL_META = {
    "name": "inverter_linear_voltage",
    "title": "线性电压依赖二次损失模型（模型38）",
    "version": "1.0.0",
    "description": (
        "Driesse 线性电压依赖二次损失模型（式62）。"
        "在双二次模型基础上去掉 Vin² 项，三个系数均为归一化输入电压 vin 的线性函数，"
        "共 6 个参数，兼顾电压依赖性与参数精简。"
    ),
    "author": "PV Team",
    "category": "逆变器",
    "related_models": {
        "pre": ["diode_model"],
        "post": [],
        "depends_on": [],
        "conflicts_with": ["inverter_quadratic", "inverter_biquadratic", "inverter_sandia"]
    },
    "inputs": [
        {
            "name": "p_in",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "归一化直流输入功率 pin（= Pdc / Prated，无量纲）"
        },
        {
            "name": "v_in",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "归一化直流输入电压 vin（= Vdc / Vrated，无量纲）"
        },
        {
            "name": "b00",
            "type": "float",
            "required": True,
            "description": "b0 的常数项（无量纲）"
        },
        {
            "name": "b01",
            "type": "float",
            "required": True,
            "description": "b0 的线性项系数（无量纲）"
        },
        {
            "name": "b10",
            "type": "float",
            "required": True,
            "description": "b1 的常数项（无量纲）"
        },
        {
            "name": "b11",
            "type": "float",
            "required": True,
            "description": "b1 的线性项系数（无量纲）"
        },
        {
            "name": "b20",
            "type": "float",
            "required": True,
            "description": "b2 的常数项（无量纲）"
        },
        {
            "name": "b21",
            "type": "float",
            "required": True,
            "description": "b2 的线性项系数（无量纲）"
        }
    ],
    "outputs": [
        {
            "name": "p_loss",
            "type": "float",
            "unit": "",
            "description": "归一化损耗 ploss（无量纲）"
        },
        {
            "name": "p_out",
            "type": "float",
            "unit": "",
            "description": "归一化交流输出功率 pout = pin - ploss（无量纲）"
        },
        {
            "name": "efficiency",
            "type": "float",
            "unit": "",
            "description": "逆变器效率 η = pout / pin"
        }
    ],
    "tags": ["inverter", "driesse", "linear-voltage", "normalized"],
    "execution": {
        "timeout": 10,
        "cacheable": True,
        "cache_ttl": 3600
    }
}
