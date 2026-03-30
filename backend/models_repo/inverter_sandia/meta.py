MODEL_META = {
    "name": "inverter_sandia",
    "title": "Sandia 逆变器模型（模型37）",
    "version": "1.0.0",
    "description": (
        "Driesse 提出的 Sandia 逆变器模型（式61）。"
        "以规格书常见参数（Paco、Pdco、Pso、Co）为基础构建，"
        "适用于参数信息不完整的场景，可逐步引入更多参数提高精度。"
    ),
    "author": "PV Team",
    "category": "逆变器",
    "related_models": {
        "pre": ["diode_model"],
        "post": [],
        "depends_on": [],
        "conflicts_with": ["inverter_quadratic", "inverter_biquadratic", "inverter_linear_voltage"]
    },
    "inputs": [
        {
            "name": "p_dc",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "直流输入功率 Pdc（W）"
        },
        {
            "name": "p_aco",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "额定交流输出功率 Paco（W）"
        },
        {
            "name": "p_dco",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "额定直流输入功率 Pdco（W）"
        },
        {
            "name": "p_so",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "启动逆变所需的自耗功率 Pso（W）"
        },
        {
            "name": "c_o",
            "type": "float",
            "required": True,
            "description": "二次修正系数 Co（1/W），描述 Pac-Pdc 曲线非线性"
        }
    ],
    "outputs": [
        {
            "name": "p_ac",
            "type": "float",
            "unit": "W",
            "description": "交流输出功率 Pac（W）"
        },
        {
            "name": "efficiency",
            "type": "float",
            "unit": "",
            "description": "逆变器效率 η = Pac / Pdc"
        },
        {
            "name": "p_loss",
            "type": "float",
            "unit": "W",
            "description": "逆变器损耗 Ploss = Pdc - Pac（W）"
        }
    ],
    "tags": ["inverter", "sandia", "driesse", "datasheet"],
    "execution": {
        "timeout": 10,
        "cacheable": True,
        "cache_ttl": 3600
    }
}
