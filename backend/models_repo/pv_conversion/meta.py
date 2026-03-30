MODEL_META = {
    "name": "pv_conversion",
    "title": "光伏转换模型",
    "version": "1.0.0",
    "description": "基于单二极管模型，计算光伏组件的输出功率与效率",
    "author": "PV Team",
    "inputs": [
        {"name": "poa_irradiance", "type": "float", "required": True,  "min": 0.0,   "description": "组件面辐照度 (W/m²)"},
        {"name": "cell_temp",      "type": "float", "required": True,  "min": -40.0, "max": 100.0, "description": "电池温度 (°C)"},
        {"name": "pdc0",           "type": "float", "required": False, "default": 250.0, "description": "STC 下额定功率 (W)"},
        {"name": "gamma_pdc",      "type": "float", "required": False, "default": -0.004, "description": "功率温度系数 (/°C)"},
    ],
    "outputs": [
        {"name": "p_dc",       "type": "float", "unit": "W",  "description": "直流输出功率"},
        {"name": "efficiency", "type": "float", "unit": "%",  "description": "转换效率"},
        {"name": "i_mp",       "type": "float", "unit": "A",  "description": "最大功率点电流"},
        {"name": "v_mp",       "type": "float", "unit": "V",  "description": "最大功率点电压"},
    ],
    "tags": ["pv", "conversion", "power"],
    "execution": {"timeout": 30, "cacheable": True, "cache_ttl": 600},
}
