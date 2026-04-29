MODEL_META = {
    "name": "pv_diode",
    "title": "光伏组件二极管模型",
    "version": "1.0.0",
    "description": "基于单二极管模型，选择组件后自动补全电学参数，计算指定工况下的输出电流与功率。",
    "author": "PV Team",
    "category": "光伏转换",
    "inputs": [
        # ── 来自组件库（UI 展示 + 自动填充，同时也会随 formData 一起发送给后端）
        {"name": "isc",        "type": "float", "required": True,  "source": "panel", "panel_field": "isc",        "description": "短路电流 (A)"},
        {"name": "voc",        "type": "float", "required": True,  "source": "panel", "panel_field": "voc",        "description": "开路电压 (V)"},
        {"name": "imp",        "type": "float", "required": True,  "source": "panel", "panel_field": "imp",        "description": "最大功率点电流 (A)"},
        {"name": "vmp",        "type": "float", "required": True,  "source": "panel", "panel_field": "vmp",        "description": "最大功率点电压 (V)"},
        {"name": "temp_coeff", "type": "float", "required": True,  "source": "panel", "panel_field": "temp_coeff", "description": "温度系数 (mA/℃)"},
        {"name": "g_ref",      "type": "float", "required": True,  "source": "panel", "panel_field": "g_ref",      "description": "参考辐照度 (W/m²)"},
        {"name": "t_ref",      "type": "float", "required": True,  "source": "panel", "panel_field": "t_ref",      "description": "参考温度 (℃)"},
        # ── 用户手动填写
        {"name": "g_poa",  "type": "float", "required": True, "min": 0,   "max": 1500, "description": "实际平面辐照度 (W/m²)"},
        {"name": "t_cell", "type": "float", "required": True, "min": -40, "max": 100,  "description": "电池温度 (℃)"},
    ],
    "outputs": [
        {"name": "current", "type": "float", "unit": "A", "description": "输出电流 I（A）"},
        {"name": "power",   "type": "float", "unit": "W", "description": "输出功率 P（W）"},
        {"name": "voc",     "type": "float", "unit": "V", "description": "开路电压 Voc（V）"},
        {"name": "isc",     "type": "float", "unit": "A", "description": "短路电流 Isc（A）"},
        {"name": "vmpp",    "type": "float", "unit": "V", "description": "最大功率点电压（V）"},
        {"name": "impp",    "type": "float", "unit": "A", "description": "最大功率点电流（A）"},
        {"name": "pmpp",    "type": "float", "unit": "W", "description": "最大功率 Pmax（W）"},
        {"name": "ff",      "type": "float", "unit": "",  "description": "填充因子 FF"},
    ],
    "tags": ["pv-diode", "panel", "single-diode"],
    "execution": {"timeout": 30, "cacheable": False},
}
