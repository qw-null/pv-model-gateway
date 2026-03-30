MODEL_META = {
    "name": "transformer_dry",
    "title": "干式变压器损失模型（模型42）",
    "version": "1.0.0",
    "description": (
        "干式变压器铁损与铜损模型（式68~69）。"
        "铁损与额定功率 P_trans_ref 准线性相关（式68）；"
        "铜损与 P_trans_ref 呈二次方关系（式69）。"
        "适用于额定功率 100~3150 kVA、最高电压不超过 36 kV 的干式变压器。"
    ),
    "author": "PV Team",
    "category": "损失模型",
    "related_models": {
        "pre": ["ac_cable_loss"],
        "post": [],
        "depends_on": [],
        "conflicts_with": ["transformer_oil"]
    },
    "inputs": [
        {
            "name": "p_trans_ref",
            "type": "float",
            "required": True,
            "min": 100.0,
            "max": 3150.0,
            "description": "额定变压器功率 P_trans_ref（kVA），范围 100~3150"
        },
        {
            "name": "beta0_prime",
            "type": "float",
            "required": True,
            "description": "铁损系数 β0'（kW），截距项"
        },
        {
            "name": "beta1_prime",
            "type": "float",
            "required": True,
            "description": "铁损系数 β1'（kW/kVA），斜率项"
        },
        {
            "name": "beta2_prime",
            "type": "float",
            "required": True,
            "description": "铜损系数 β2'（kW/kVA），一次项"
        },
        {
            "name": "beta3_prime",
            "type": "float",
            "required": True,
            "description": "铜损系数 β3'（kW/kVA²），二次项"
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
    "tags": ["transformer", "dry-type", "iron-loss", "copper-loss"],
    "execution": {
        "timeout": 10,
        "cacheable": True,
        "cache_ttl": 3600
    }
}
