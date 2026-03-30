MODEL_META = {
    "name": "irradiance_split",
    "title": "辐照分离模型",
    "version": "1.0.0",
    "description": "将水平面总辐照度（GHI）分离为直接辐照（DNI）和散射辐照（DHI）",
    "author": "PV Team",
    "inputs": [
        {
            "name": "ghi",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "水平面总辐照度 (W/m²)"
        },
        {
            "name": "solar_zenith",
            "type": "float",
            "required": True,
            "min": 0.0,
            "max": 90.0,
            "description": "太阳天顶角 (°)"
        },
        {
            "name": "datetime",
            "type": "str",
            "required": True,
            "description": "ISO 格式时间"
        },
        {
            "name": "method",
            "type": "enum",
            "options": ["erbs", "boland", "disc"],
            "required": False,
            "default": "erbs",
            "description": "分离算法选择"
        },
    ],
    "outputs": [
        {"name": "dni", "type": "float", "unit": "W/m²", "description": "直接法线辐照度"},
        {"name": "dhi", "type": "float", "unit": "W/m²", "description": "散射水平辐照度"},
        {"name": "kt",  "type": "float", "unit": "",     "description": "晴空指数"},
    ],
    "tags": ["irradiance", "split", "solar"],
    "execution": {"timeout": 30, "cacheable": True, "cache_ttl": 1800},
}
