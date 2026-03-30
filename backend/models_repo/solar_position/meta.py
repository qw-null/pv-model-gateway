MODEL_META = {
    "name":        "solar_position",
    "title":       "太阳位置模型",
    "version":     "1.0.0",
    "description": "根据时间和地理坐标，计算太阳高度角、方位角与天顶角",
    "author":      "PV Team",
    "category":    "太阳位置",
    "inputs": [
        {
            "name":        "latitude",
            "type":        "float",
            "required":    True,
            "min":         -90.0,
            "max":         90.0,
            "description": "纬度 (°)"
        },
        {
            "name":        "longitude",
            "type":        "float",
            "required":    True,
            "min":         -180.0,
            "max":         180.0,
            "description": "经度 (°)"
        },
        {
            "name":        "datetime",
            "type":        "str",
            "format":      "datetime",
            "required":    True,
            "description": "ISO 格式时间，如 2024-06-21T12:00:00"
        },
        {
            "name":        "timezone",
            "type":        "str",
            "required":    False,
            "default":     "Asia/Shanghai",
            "description": "时区字符串，如 Asia/Shanghai"
        },
    ],
    "outputs": [
        {"name": "altitude",   "type": "float", "unit": "°", "description": "太阳高度角"},
        {"name": "azimuth",    "type": "float", "unit": "°", "description": "太阳方位角"},
        {"name": "zenith",     "type": "float", "unit": "°", "description": "天顶角"},
        {"name": "is_daytime", "type": "bool",  "unit": "",  "description": "是否为白天"},
    ],
    "tags": ["solar", "position", "geometry"],
    "execution": {
        "timeout":   30,
        "cacheable": True,
        "cache_ttl": 3600,
    },
}
