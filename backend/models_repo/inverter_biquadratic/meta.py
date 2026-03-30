MODEL_META = {
    "name": "inverter_biquadratic",
    "title": "逆变器双二次损失模型（模型36）",
    "version": "1.0.0",
    "description": (
        "Driesse 双二次损失模型（式60）。"
        "在二次函数模型基础上，引入输入电压 Vin 对三个系数的影响，"
        "每个系数 ai 均为 Vin 的二次多项式，共 9 个参数。"
    ),
    "author": "PV Team",
    "category": "逆变器",
    "related_models": {
        "pre": ["diode_model"],
        "post": [],
        "depends_on": [],
        "conflicts_with": ["inverter_quadratic", "inverter_sandia", "inverter_linear_voltage"]
    },
    "inputs": [
        {
            "name": "p_out",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "交流输出功率 Pout（W）"
        },
        {
            "name": "v_in",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "直流输入电压 Vin（V）"
        },
        {
            "name": "a00",
            "type": "float",
            "required": True,
            "description": "a0 的常数项（W）"
        },
        {
            "name": "a01",
            "type": "float",
            "required": True,
            "description": "a0 的一次项系数（W/V）"
        },
        {
            "name": "a02",
            "type": "float",
            "required": True,
            "description": "a0 的二次项系数（W/V²）"
        },
        {
            "name": "a10",
            "type": "float",
            "required": True,
            "description": "a1 的常数项（无量纲）"
        },
        {
            "name": "a11",
            "type": "float",
            "required": True,
            "description": "a1 的一次项系数（1/V）"
        },
        {
            "name": "a12",
            "type": "float",
            "required": True,
            "description": "a1 的二次项系数（1/V²）"
        },
        {
            "name": "a20",
            "type": "float",
            "required": True,
            "description": "a2 的常数项（1/W）"
        },
        {
            "name": "a21",
            "type": "float",
            "required": True,
            "description": "a2 的一次项系数（1/(W·V)）"
        },
        {
            "name": "a22",
            "type": "float",
            "required": True,
            "description": "a2 的二次项系数（1/(W·V²)）"
        }
    ],
    "outputs": [
        {
            "name": "p_loss",
            "type": "float",
            "unit": "W",
            "description": "逆变器总损耗 Ploss（W）"
        },
        {
            "name": "p_in",
            "type": "float",
            "unit": "W",
            "description": "直流输入功率 Pin = Pout + Ploss（W）"
        },
        {
            "name": "efficiency",
            "type": "float",
            "unit": "",
            "description": "逆变器效率 η = Pout / Pin"
        }
    ],
    "tags": ["inverter", "driesse", "biquadratic", "voltage-dependent"],
    "execution": {
        "timeout": 10,
        "cacheable": True,
        "cache_ttl": 3600
    }
}
