# backend/models_repo/inverter_from_ond/meta.py

MODEL_META = {
    "name":        "inverter_from_ond",
    "title":       "逆变器模型（OND 数据库驱动）",
    "version":     "1.0.0",
    "description": (
        "基于 OND 文件导入的逆变器数据库，自动补全 Sandia 模型参数（Paco/Pdco/Pso/Co），"
        "只需提供逆变器 ID 和实际直流输入功率 Pdc 即可完成计算。"
        "底层使用与 inverter_sandia 完全相同的 Driesse 式61公式。"
    ),
    "author":   "PV Team",
    "category": "逆变器",
    "related_models": {
        "pre":           ["pv_diode", "inverter_from_ond"],
        "post":          [],
        "depends_on":    [],
        "conflicts_with":["inverter_sandia", "inverter_king",
                          "inverter_biquadratic", "inverter_quadratic",
                          "inverter_linear_voltage"]
    },
    "inputs": [
        # ── 来自逆变器数据库（UI 展示 + 自动填充）──────────────
        {
            "name": "p_aco", "type": "float", "required": True,
            "source": "inverter", "inverter_field": "p_aco",
            "description": "额定交流输出功率 Paco（W）"
        },
        {
            "name": "p_dco", "type": "float", "required": True,
            "source": "inverter", "inverter_field": "p_dco",
            "description": "额定直流输入功率 Pdco（W，效率曲线拟合值）"
        },
        {
            "name": "p_so", "type": "float", "required": True,
            "source": "inverter", "inverter_field": "p_so",
            "description": "启动自耗功率 Pso（W，效率曲线拟合值）"
        },
        {
            "name": "c_o", "type": "float", "required": True,
            "source": "inverter", "inverter_field": "c_o",
            "description": "二次修正系数 Co（1/W，效率曲线拟合值）"
        },
        # ── 用户手动输入 ────────────────────────────────────────
        {
            "name": "p_dc", "type": "float", "required": True,
            "min": 0.0,
            "description": "实际直流输入功率 Pdc（W）"
        },
    ],
    "outputs": [
        {
            "name": "p_ac", "type": "float", "unit": "W",
            "description": "交流输出功率 Pac（W）"
        },
        {
            "name": "efficiency", "type": "float", "unit": "",
            "description": "逆变器效率 η = Pac / Pdc"
        },
        {
            "name": "p_loss", "type": "float", "unit": "W",
            "description": "逆变器损耗 Ploss = Pdc - Pac（W）"
        },
    ],
    "tags": ["inverter", "sandia", "ond", "database-driven"],
    "execution": {"timeout": 10, "cacheable": True, "cache_ttl": 3600},
}
