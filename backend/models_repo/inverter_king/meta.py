MODEL_META = {
    "name": "inverter_king",
    "title": "King 逆变器效率模型（模型34）",
    "version": "1.0.0",
    "description": (
        "King 等人提出的逆变器交流输出功率模型（式59~62）。"
        "以直流输入电压和功率为输入，通过四个经验系数 C0~C3 "
        "计算逆变器的交流输出功率，适用于 Sandia 数据库参数体系。"
    ),
    "author": "PV Team",
    "category": "逆变器",
    "related_models": {
        "pre": ["diode_model"],
        "post": [],
        "depends_on": [],
        "conflicts_with": []
    },
    "inputs": [
        {
            "name": "p_dc",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "逆变器直流输入功率 Pdc（W）"
        },
        {
            "name": "v_dc",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "逆变器直流输入电压 Vdc（V）"
        },
        {
            "name": "p_ac_ref",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "额定交流输出功率 Pac_ref（W）"
        },
        {
            "name": "p_dc_ref",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "实现额定交流功率所需的直流功率 Pdc_ref（W）"
        },
        {
            "name": "v_dc_ref",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "实现额定交流功率时的直流电压 Vdc_ref（V）"
        },
        {
            "name": "p_s_ref",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "启动逆变过程所需的最小直流功率 Ps_ref（W）"
        },
        {
            "name": "c0",
            "type": "float",
            "required": True,
            "description": "经验系数 C0（1/W），描述 Pac-Pdc 曲线的二次项"
        },
        {
            "name": "c1",
            "type": "float",
            "required": True,
            "description": "经验系数 C1（1/V），Pdc_ref 的电压修正系数"
        },
        {
            "name": "c2",
            "type": "float",
            "required": True,
            "description": "经验系数 C2（1/V），Ps_ref 的电压修正系数"
        },
        {
            "name": "c3",
            "type": "float",
            "required": True,
            "description": "经验系数 C3（1/V），C0 的电压修正系数"
        }
    ],
    "outputs": [
        {
            "name": "p_ac",
            "type": "float",
            "unit": "W",
            "description": "逆变器交流输出功率 Pac（W）"
        },
        {
            "name": "efficiency",
            "type": "float",
            "unit": "",
            "description": "逆变器效率 η = Pac / Pdc"
        },
        {
            "name": "p_loss",
            "type": "float",
            "unit": "W",
            "description": "逆变器损耗 Ploss = Pdc - Pac（W）"
        }
    ],
    "tags": ["inverter", "king", "sandia", "efficiency"],
    "execution": {
        "timeout": 10,
        "cacheable": True,
        "cache_ttl": 3600
    }
}
