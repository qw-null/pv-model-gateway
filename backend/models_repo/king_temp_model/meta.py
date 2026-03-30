MODEL_META = {
    "name": "king_temp_model",
    "title": "King 电池温度模型（模型26~27）",
    "version": "1.0.0",
    "description": (
        "King 等人提出的非线性电池温度模型。"
        "式(49) 计算组件温度：Tmod = Gc * exp(a + b*W) + Tamb；"
        "式(48) 在组件温度基础上加电池与组件温差：Tcell = Tmod + Gc/1000 * ΔT。"
        "系数 a、b、ΔT 取决于组件封装和安装方式。"
    ),
    "author": "PV Team",
    "category": "电池温度",
    "related_models": {
        "pre": ["solar_position", "perez_model"],
        "post": [],
        "depends_on": [],
        "conflicts_with": [
            "linear_temp_model",
            "faiman_temp_model"
        ]
    },
    "inputs": [
        {
            "name": "tamb",
            "type": "float",
            "required": True,
            "min": -50.0,
            "max": 60.0,
            "description": "环境温度 Tamb（°C）"
        },
        {
            "name": "gc",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "入射有效辐照度 Gc（W/m²）"
        },
        {
            "name": "wind_speed",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "风速 W（m/s）"
        },
        {
            "name": "a",
            "type": "float",
            "required": False,
            "default": -3.56,
            "description": "封装系数 a，开放支架玻璃/电池/聚合物背板典型值 -3.56"
        },
        {
            "name": "b",
            "type": "float",
            "required": False,
            "default": -0.075,
            "description": "风速系数 b，典型值 -0.075"
        },
        {
            "name": "delta_t",
            "type": "float",
            "required": False,
            "default": 3.0,
            "description": "电池与组件温差 ΔT（°C），典型值 3.0"
        }
    ],
    "outputs": [
        {
            "name": "t_cell",
            "type": "float",
            "unit": "°C",
            "description": "电池温度 Tcell（°C）"
        },
        {
            "name": "t_mod",
            "type": "float",
            "unit": "°C",
            "description": "组件温度 Tmod（°C）"
        }
    ],
    "tags": ["temperature", "king", "nonlinear", "cell", "module"],
    "execution": {
        "timeout": 10,
        "cacheable": True,
        "cache_ttl": 1800
    }
}
