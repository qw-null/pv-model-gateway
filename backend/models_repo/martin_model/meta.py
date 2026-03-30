MODEL_META = {
    "name": "martin_model",
    "title": "Martin 反射损失模型（模型18~20）",
    "version": "1.0.0",
    "description": (
        "Martin & Ruiz 2001 提出的半经验反射损失模型。"
        "分别计算直接辐射（τb）、漫射辐射（τd）和地面反射辐射（τg）的相对透过率，"
        "输出考虑反射损失后的有效吸收辐照度 Geff。"
        "主要参数为组件封装相关系数 ar（反射系数）。"
    ),
    "author": "PV Team",
    "category": "光学修正",
    "related_models": {
        "pre": ["solar_position", "perez_model"],
        "post": [],
        "depends_on": [],
        "conflicts_with": ["physical_beam_model", "xie_model"]
    },
    "inputs": [
        {
            "name": "bc",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "倾斜面直接辐照度 Bc（W/m²），来自转换模型"
        },
        {
            "name": "dc",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "倾斜面漫射辐照度 Dc（W/m²），来自转换模型"
        },
        {
            "name": "dg",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "地面反射辐照度 Dg（W/m²），来自转换模型"
        },
        {
            "name": "aoi",
            "type": "float",
            "required": True,
            "min": 0.0,
            "max": 90.0,
            "description": "直接辐射入射角 AOI（°），太阳光线与组件法线夹角"
        },
        {
            "name": "surface_tilt",
            "type": "float",
            "required": True,
            "min": 0.0,
            "max": 90.0,
            "description": "组件倾斜角 S（°）"
        },
        {
            "name": "ar",
            "type": "float",
            "required": False,
            "min": 0.0,
            "max": 0.5,
            "default": 0.16,
            "description": "封装反射系数 ar，与组件封装设计相关，默认 0.16"
        },
        {
            "name": "c1",
            "type": "float",
            "required": False,
            "min": 0.0,
            "default": 0.4244,
            "description": "漫射积分系数 c1 = 4/(3π) ≈ 0.4244，一般不需修改"
        }
    ],
    "outputs": [
        {
            "name": "tau_b",
            "type": "float",
            "unit": "",
            "description": "直接辐射相对透过率 τb"
        },
        {
            "name": "tau_d",
            "type": "float",
            "unit": "",
            "description": "漫射辐射相对透过率 τd"
        },
        {
            "name": "tau_g",
            "type": "float",
            "unit": "",
            "description": "地面反射辐射相对透过率 τg"
        },
        {
            "name": "geff",
            "type": "float",
            "unit": "W/m²",
            "description": "有效吸收辐照度 Geff = τb*Bc + τd*Dc + τg*Dg"
        }
    ],
    "tags": ["martin", "reflection", "transmittance", "IAM"],
    "execution": {
        "timeout": 10,
        "cacheable": True,
        "cache_ttl": 1800
    }
}
