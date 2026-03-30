MODEL_META = {
    "name": "physical_beam_model",
    "title": "物理光束透过率模型（模型21）",
    "version": "1.0.0",
    "description": (
        "基于 Fresnel 定律的物理光束透过率模型。"
        "同时考虑玻璃界面处的反射损耗和玻璃内部的吸收损耗，"
        "计算直接辐射的相对透过率 τb。"
        "漫射和地面反射透过率由 Xie 模型提供更精确的计算。"
    ),
    "author": "PV Team",
    "category": "光学修正",
    "related_models": {
        "pre": ["solar_position", "perez_model"],
        "post": [],
        "depends_on": [],
        "conflicts_with": ["martin_model"]
    },
    "inputs": [
        {
            "name": "bc",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "倾斜面直接辐照度 Bc（W/m²）"
        },
        {
            "name": "aoi",
            "type": "float",
            "required": True,
            "min": 0.0,
            "max": 90.0,
            "description": "直接辐射入射角 AOI（°）"
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
            "description": "玻璃消光系数 K（m⁻¹），标准值约 4.0"
        },
        {
            "name": "L",
            "type": "float",
            "required": False,
            "min": 0.0,
            "default": 0.002,
            "description": "玻璃厚度 L（m），标准值约 2mm=0.002m"
        }
    ],
    "outputs": [
        {
            "name": "tau_b",
            "type": "float",
            "unit": "",
            "description": "直接辐射物理透过率 τb（含反射损耗和吸收损耗）"
        },
        {
            "name": "tau_b_reflection",
            "type": "float",
            "unit": "",
            "description": "仅反射损耗的透过率分量"
        },
        {
            "name": "tau_b_absorption",
            "type": "float",
            "unit": "",
            "description": "仅吸收损耗的透过率分量"
        },
        {
            "name": "theta_r",
            "type": "float",
            "unit": "°",
            "description": "折射角（°）"
        },
        {
            "name": "geff_b",
            "type": "float",
            "unit": "W/m²",
            "description": "修正后的直接辐照度 Geff_b = τb * Bc"
        }
    ],
    "tags": ["fresnel", "physical", "reflection", "transmittance", "beam"],
    "execution": {
        "timeout": 10,
        "cacheable": True,
        "cache_ttl": 1800
    }
}
