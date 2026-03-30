MODEL_META = {
    "name": "dc_cable_loss",
    "title": "直流电缆损失模型（模型39）",
    "version": "1.0.0",
    "description": (
        "基于欧姆定律计算光伏阵列直流侧电缆功率损失（式63）。"
        "利用 MPP 工作点电流、电缆等效电阻及阵列拓扑参数，"
        "计算直流侧欧姆损失及其占 MPP 功率的比例。"
    ),
    "author": "PV Team",
    "category": "损失模型",
    "related_models": {
        "pre": ["diode_model"],
        "post": ["inverter_king"],
        "depends_on": [],
        "conflicts_with": []
    },
    "inputs": [
        {
            "name": "ns",
            "type": "int",
            "required": True,
            "min": 1,
            "description": "串联组件数 Ns"
        },
        {
            "name": "np",
            "type": "int",
            "required": True,
            "min": 1,
            "description": "并联组串数 Np"
        },
        {
            "name": "r_dc_wire",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "直流电缆等效电阻 R_dc_wire（Ω）"
        },
        {
            "name": "i_mpp",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "MPP 工作点电流 Impp（A）"
        },
        {
            "name": "v_mpp",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "MPP 工作点电压 Vmpp（V）"
        }
    ],
    "outputs": [
        {
            "name": "p_mpp",
            "type": "float",
            "unit": "W",
            "description": "阵列 MPP 总功率 Pmpp = Ns × Np × Vmpp × Impp（W）"
        },
        {
            "name": "p_dc_loss",
            "type": "float",
            "unit": "W",
            "description": "直流电缆欧姆损失 P_dc_loss（W）"
        },
        {
            "name": "loss_ratio",
            "type": "float",
            "unit": "",
            "description": "直流电缆损失率 L_dc = P_dc_loss / Pmpp"
        },
        {
            "name": "p_dc_out",
            "type": "float",
            "unit": "W",
            "description": "直流侧净输出功率 P_dc_out = Pmpp - P_dc_loss（W）"
        }
    ],
    "tags": ["dc-cable", "ohmic-loss", "wiring", "pv-system"],
    "execution": {
        "timeout": 10,
        "cacheable": True,
        "cache_ttl": 3600
    }
}
