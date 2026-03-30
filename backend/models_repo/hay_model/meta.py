MODEL_META = {
    "name": "hay_model",
    "title": "Hay 转换模型（模型12）",
    "version": "1.0.0",
    "description": (
        "Hay 等人在各向同性模型基础上引入各向异性指数 Ai，"
        "将漫射辐射分为环日分量和各向同性背景两部分，"
        "是 Perez 模型出现前最常用的转换模型之一。"
        "GTI = Bc + Dc + Dg"
    ),
    "author": "PV Team",
    "category": "光伏转换",
    "related_models": {
        "pre": ["solar_position", "engerer_model"],
        "post": [],
        "depends_on": [],
        "conflicts_with": []
    },
    "inputs": [
        {
            "name": "ghi",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "水平面总辐照度 GHI（W/m²）"
        },
        {
            "name": "dhi",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "漫射水平辐照度 DHI（W/m²）"
        },
        {
            "name": "bni",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "直接法向辐照度 BNI（W/m²）"
        },
        {
            "name": "solar_zenith",
            "type": "float",
            "required": True,
            "min": 0.0,
            "max": 90.0,
            "description": "太阳天顶角 Z（°）"
        },
        {
            "name": "solar_azimuth",
            "type": "float",
            "required": True,
            "min": 0.0,
            "max": 360.0,
            "description": "太阳方位角（°，北=0，顺时针）"
        },
        {
            "name": "surface_tilt",
            "type": "float",
            "required": True,
            "min": 0.0,
            "max": 90.0,
            "description": "组件倾斜角 S（°，水平=0，垂直=90）"
        },
        {
            "name": "surface_azimuth",
            "type": "float",
            "required": True,
            "min": 0.0,
            "max": 360.0,
            "description": "组件朝向方位角（°，正南=180）"
        },
        {
            "name": "albedo",
            "type": "float",
            "required": False,
            "min": 0.0,
            "max": 1.0,
            "default": 0.2,
            "description": "地表反照率 ρ，默认 0.2"
        },
        {
            "name": "dni_extra",
            "type": "float",
            "required": False,
            "min": 0.0,
            "default": 1367.0,
            "description": "大气层外法向辐照度 E0（W/m²），默认 1367.0"
        }
    ],
    "outputs": [
        {
            "name": "gti",
            "type": "float",
            "unit": "W/m²",
            "description": "倾斜面总辐照度 GTI = Bc + Dc + Dg"
        },
        {
            "name": "bc",
            "type": "float",
            "unit": "W/m²",
            "description": "倾斜面直接辐照度 Bc"
        },
        {
            "name": "dc",
            "type": "float",
            "unit": "W/m²",
            "description": "倾斜面漫射辐照度 Dc（含各向异性修正）"
        },
        {
            "name": "dg",
            "type": "float",
            "unit": "W/m²",
            "description": "地面反射辐照度 Dg"
        },
        {
            "name": "ai",
            "type": "float",
            "unit": "",
            "description": "Hay 各向异性指数 Ai = BNI / E0"
        }
    ],
    "tags": ["hay", "transposition", "anisotropic"],
    "execution": {
        "timeout": 10,
        "cacheable": True,
        "cache_ttl": 1800
    }
}
