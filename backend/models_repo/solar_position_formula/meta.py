MODEL_META = {
    "id":1,
    "name": "solar_position_formula",
    "title": "太阳位置模型_公式法（模型1）",
    "version": "1.0.0",
    "description": "基于球面天文学公式计算太阳高度角、方位角与天顶角",
    "author": "PV Team",
    "category":    "太阳位置",
    "inputs": [
        {
            "name": "L",
            "type": "float",
            "required": True,
            "min": -90.0,
            "max": 90.0,
            "description": "观测点纬度 L (°)"
        },
        {
            "name": "delta",
            "type": "float",
            "required": True,
            "min": -23.45,
            "max": 23.45,
            "description": "太阳赤纬 δ (°)"
        },
        {
            "name": "H",
            "type": "float",
            "required": True,
            "min": -180.0,
            "max": 180.0,
            "description": "时角 H (°)"
        },
    ],
    "outputs": [
        {"name": "alpha",     "type": "float", "unit": "°", "description": "太阳高度角"},
        {"name": "phi_s",     "type": "float", "unit": "°", "description": "太阳方位角"},
        {"name": "Z",         "type": "float", "unit": "°", "description": "天顶角"},
        {"name": "is_daytime","type": "bool",  "unit": "",  "description": "是否为白天"},
    ],
    "tags": ["solar", "position", "formula"],
    "execution": {
        "timeout": 10,
        "cacheable": True,
        "cache_ttl": 3600,
    },
}
