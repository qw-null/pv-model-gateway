MODEL_META = {
    "name": "ac_cable_loss",
    "title": "交流电缆损失模型（模型40）",
    "version": "1.0.0",
    "description": (
        "计算逆变器至变压器之间交流电缆的功率损失（式64~65）。"
        "式64 由电缆材料参数计算等效电阻；"
        "式65 计算三相交流欧姆损失功率。"
        "支持单相和三相两种接线方式。"
    ),
    "author": "PV Team",
    "category": "损失模型",
    "related_models": {
        "pre": ["inverter_king"],
        "post": ["transformer_oil", "transformer_dry"],
        "depends_on": [],
        "conflicts_with": []
    },
    "inputs": [
        {
            "name": "rho",
            "type": "float",
            "required": False,
            "default": 1.72e-8,
            "description": "导体电阻率 ρ（Ω·m），铜默认 1.72e-8，铝约 2.82e-8"
        },
        {
            "name": "length",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "单根电缆长度 l（m）"
        },
        {
            "name": "cross_section",
            "type": "float",
            "required": True,
            "min": 1e-6,
            "description": "电缆截面积 S（m²），例如 35mm² 传入 35e-6"
        },
        {
            "name": "i_ac",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "交流侧线电流有效值 Iac（A）"
        },
        {
            "name": "phases",
            "type": "int",
            "required": False,
            "default": 3,
            "options": [1, 3],
            "description": "相数：1（单相）或 3（三相），默认 3"
        }
    ],
    "outputs": [
        {
            "name": "r_ac_wire",
            "type": "float",
            "unit": "Ω",
            "description": "交流电缆单相等效电阻 R_ac_wire（Ω）"
        },
        {
            "name": "p_ac_loss",
            "type": "float",
            "unit": "W",
            "description": "交流电缆总损失功率 P_ac_loss（W）"
        }
    ],
    "tags": ["ac-cable", "ohmic-loss", "wiring", "pv-system"],
    "execution": {
        "timeout": 10,
        "cacheable": True,
        "cache_ttl": 3600
    }
}
