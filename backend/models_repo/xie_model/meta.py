MODEL_META = {
    "name": "xie_model",
    "title": "Xie 漫射/地面反射透过率模型（模型22~23）",
    "version": "1.0.0",
    "description": (
        "Xie 等人 2022 年提出的基于 Fresnel 定律的解析模型，"
        "分别计算漫射辐射（τd，式43）和地面反射辐射（τg，式45）的相对透过率。"
        "τd 通过对半球方向积分得到解析表达式，"
        "τg 考虑地面反射的等效入射角分布。"
    ),
    "author": "PV Team",
    "category": "光学修正",
    "related_models": {
        "pre": ["solar_position", "perez_model", "physical_beam_model"],
        "post": [],
        "depends_on": [],
        "conflicts_with": ["martin_model"]
    },
    "inputs": [
        {
            "name": "dc",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "倾斜面漫射辐照度 Dc（W/m²）"
        },
        {
            "name": "dg",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "地面反射辐照度 Dg（W/m²）"
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
            "name": "n1",
            "type": "float",
            "required": False,
            "min": 1.0,
            "default": 1.0,
            "description": "入射介质折射率 n1（空气=1.0）"
        },
        {
            "name": "n2",
            "type": "float",
            "required": False,
            "min": 1.0,
            "default": 1.526,
            "description": "玻璃折射率 n2，标准低铁玻璃约 1.526"
        },
        {
            "name": "K",
            "type": "float",
            "required": False,
            "min": 0.0,
            "default": 4.0,
            "description": "玻璃消光系数 K（m⁻¹）"
        },
        {
            "name": "L",
            "type": "float",
            "required": False,
            "min": 0.0,
            "default": 0.002,
            "description": "玻璃厚度 L（m）"
        }
    ],
    "outputs": [
        {
            "name": "tau_d",
            "type": "float",
            "unit": "",
            "description": "漫射辐射相对透过率 τd（Xie 2022 解析式）"
        },
        {
            "name": "tau_g",
            "type": "float",
            "unit": "",
            "description": "地面反射辐射相对透过率 τg（Xie 2022 解析式）"
        },
        {
            "name": "geff_d",
            "type": "float",
            "unit": "W/m²",
            "description": "修正后漫射辐照度 Geff_d = τd * Dc"
        },
        {
            "name": "geff_g",
            "type": "float",
            "unit": "W/m²",
            "description": "修正后地面反射辐照度 Geff_g = τg * Dg"
        }
    ],
    "tags": ["xie", "fresnel", "diffuse", "ground", "transmittance"],
    "execution": {
        "timeout": 10,
        "cacheable": True,
        "cache_ttl": 1800
    }
}
