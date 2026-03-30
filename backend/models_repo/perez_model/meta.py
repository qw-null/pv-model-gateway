MODEL_META = {
    "name": "perez_model",
    "title": "Perez 转换模型（模型13~17）",
    "version": "1.0.0",
    "description": (
        "Perez 系列转换模型，包含 1986/1987/1988/1990a/1990b 五个版本。"
        "基于天空透明度参数 ε 和天空亮度参数 Δ，"
        "通过 F1/F2 系数对环日分量和地平线亮带进行精细建模。"
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
        },
        {
            "name": "model_type",
            "type": "enum",
            "required": False,
            "default": "perez1990a",
            "options": [
                "perez1986",
                "perez1987",
                "perez1988",
                "perez1990a",
                "perez1990b"
            ],
            "description": "Perez 模型版本，默认 perez1990a（部分多云最优）"
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
            "description": "倾斜面漫射辐照度 Dc（含环日和地平线亮带）"
        },
        {
            "name": "dg",
            "type": "float",
            "unit": "W/m²",
            "description": "地面反射辐照度 Dg"
        },
        {
            "name": "f1",
            "type": "float",
            "unit": "",
            "description": "环日亮度系数 F1"
        },
        {
            "name": "f2",
            "type": "float",
            "unit": "",
            "description": "地平线亮度系数 F2"
        },
        {
            "name": "epsilon",
            "type": "float",
            "unit": "",
            "description": "天空透明度参数 ε"
        },
        {
            "name": "delta",
            "type": "float",
            "unit": "",
            "description": "天空亮度参数 Δ"
        }
    ],
    "tags": ["perez", "transposition", "anisotropic"],
    "execution": {
        "timeout": 10,
        "cacheable": True,
        "cache_ttl": 1800
    }
}
