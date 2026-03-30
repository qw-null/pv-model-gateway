MODEL_META = {
    "name": "transformer_oil",
    "title": "油浸式变压器损失模型（模型41）",
    "version": "1.0.0",
    "description": (
        "油浸式变压器铁损与铜损模型（式66~67）。"
        "铁损（磁滞+涡流）和铜损（绕组电阻）均与额定功率 P_trans_ref 准线性相关。"
        "适用于额定功率 50~2500 kVA、最高电压不超过 36 kV 的油浸式变压器。"
    ),
    "author": "PV Team",
    "category": "损失模型",
    "related_models": {
        "pre": ["ac_cable_loss"],
        "post": [],
        "depends_on": [],
        "conflicts_with": ["transformer_dry"]
    },
    "inputs": [
        {
            "name": "p_trans_ref",
            "type": "float",
            "required": True,
            "min": 50.0,
            "max": 2500.0,
            "description": "额定变压器功率 P_trans_ref（kVA），范围 50~2500"
        },
        {
            "name": "beta0",
            "type": "float",
            "required": True,
            "description": "铁损系数 β0（kW），截距项"
        },
        {
            "name": "beta1",
            "type": "float",
            "required": True,
            "description": "铁损系数 β1（kW/kVA），斜率项"
        },
        {
            "name": "beta2",
            "type": "float",
            "required": True,
            "description": "铜损系数 β2（kW/kVA），斜率项"
        },
        {
            "name": "load_factor",
            "type": "float",
            "required": False,
            "default": 1.0,
            "min": 0.0,
            "max": 1.0,
            "description": "负载率 k（0~1），铜损随负载率平方变化，默认满载 1.0"
        }
    ],
    "outputs": [
        {
            "name": "p_fe",
            "type": "float",
            "unit": "kW",
            "description": "铁损 P_Fe（kW）"
        },
        {
            "name": "p_cu",
            "type": "float",
            "unit": "kW",
            "description": "铜损 P_Cu（kW），含负载率修正"
        },
        {
            "name": "p_loss_total",
            "type": "float",
            "unit": "kW",
            "description": "变压器总损失 P_loss = P_Fe + P_Cu（kW）"
        },
        {
            "name": "efficiency",
            "type": "float",
            "unit": "",
            "description": "变压器效率 η = P_out / (P_out + P_loss)"
        }
    ],
    "tags": ["transformer", "oil-immersed", "iron-loss", "copper-loss"],
    "execution": {
        "timeout": 10,
        "cacheable": True,
        "cache_ttl": 3600
    }
}
