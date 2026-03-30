MODEL_META = {
    "name": "isotropic_model",
    "title": "各向同性转换模型（模型11）",
    "version": "1.0.0",
    "description": (
        "Liu-Jordan 1963 提出的经典各向同性转换模型。"
        "假设天空漫射辐射各向同性均匀分布，"
        "将 GHI/DHI/BNI 转换为倾斜面总辐照度 GTI。"
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
            "description": "倾斜面漫射辐照度 Dc = DHI * (1+cos(S))/2"
        },
        {
            "name": "dg",
            "type": "float",
            "unit": "W/m²",
            "description": "地面反射辐照度 Dg = GHI * albedo * (1-cos(S))/2"
        }
    ],
    "tags": ["isotropic", "transposition", "liu-jordan"],
    "execution": {
        "timeout": 10,
        "cacheable": True,
        "cache_ttl": 1800
    }
}
