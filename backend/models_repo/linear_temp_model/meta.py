MODEL_META = {
    "name": "linear_temp_model",
    "title": "线性电池温度模型（模型24~25）",
    "version": "1.0.0",
    "description": (
        "显式线性电池温度模型。"
        "模型24为通用线性形式：Tcell = β0 + β1*Tamb + β2*Gc + β3*W；"
        "模型25为 NOCT 等价形式：Tcell = Tamb + (NOCT-20)/800 * Gc。"
        "系数随组件位置、材料、封装和安装类型变化。"
    ),
    "author": "PV Team",
    "category": "电池温度",
    "related_models": {
        "pre": ["solar_position", "perez_model"],
        "post": [],
        "depends_on": [],
        "conflicts_with": [
            "king_temp_model",
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
            "required": False,
            "min": 0.0,
            "default": 1.0,
            "description": "风速 W（m/s），默认 1.0"
        },
        {
            "name": "model_type",
            "type": "enum",
            "required": False,
            "default": "noct",
            "options": ["general", "noct"],
            "description": "模型类型：general（通用线性）/ noct（NOCT等价形式）"
        },
        {
            "name": "beta0",
            "type": "float",
            "required": False,
            "default": 0.0,
            "description": "通用线性模型系数 β0（截距），仅 general 模式使用"
        },
        {
            "name": "beta1",
            "type": "float",
            "required": False,
            "default": 1.0,
            "description": "通用线性模型系数 β1（Tamb 权重），仅 general 模式使用"
        },
        {
            "name": "beta2",
            "type": "float",
            "required": False,
            "default": 0.03,
            "description": "通用线性模型系数 β2（Gc 权重），仅 general 模式使用"
        },
        {
            "name": "beta3",
            "type": "float",
            "required": False,
            "default": 0.0,
            "description": "通用线性模型系数 β3（风速权重），仅 general 模式使用"
        },
        {
            "name": "noct",
            "type": "float",
            "required": False,
            "min": 20.0,
            "max": 80.0,
            "default": 45.0,
            "description": "名义运行电池温度 NOCT（°C），仅 noct 模式使用，默认 45°C"
        }
    ],
    "outputs": [
        {
            "name": "t_cell",
            "type": "float",
            "unit": "°C",
            "description": "电池温度 Tcell（°C）"
        }
    ],
    "tags": ["temperature", "linear", "NOCT", "cell"],
    "execution": {
        "timeout": 10,
        "cacheable": True,
        "cache_ttl": 1800
    }
}
