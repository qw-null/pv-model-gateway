MODEL_META = {
    "name": "inverter_quadratic",
    "title": "逆变器二次函数损失模型（模型35）",
    "version": "1.0.0",
    "description": (
        "Driesse 二次函数损失模型（式59）。"
        "损耗分三项：a0 固定自耗、a1 线性（压降）损耗、a2 欧姆损耗，"
        "仅依赖输出功率，不考虑输入电压影响。"
    ),
    "author": "PV Team",
    "category": "逆变器",
    "related_models": {
        "pre": ["diode_model"],
        "post": [],
        "depends_on": [],
        "conflicts_with": ["inverter_biquadratic", "inverter_sandia", "inverter_linear_voltage"]
    },
    "inputs": [
        {
            "name": "p_out",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "逆变器交流输出功率 Pout（W）"
        },
        {
            "name": "a0",
            "type": "float",
            "required": True,
            "description": "固定自耗系数 a0（W），对应控制/驱动电路固定功耗"
        },
        {
            "name": "a1",
            "type": "float",
            "required": True,
            "description": "线性损耗系数 a1（无量纲），对应半导体固定压降损耗"
        },
        {
            "name": "a2",
            "type": "float",
            "required": True,
            "description": "二次损耗系数 a2（1/W），对应欧姆损耗"
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
    "tags": ["inverter", "driesse", "quadratic", "loss"],
    "execution": {
        "timeout": 10,
        "cacheable": True,
        "cache_ttl": 3600
    }
}
