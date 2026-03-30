MODEL_META = {
    "name": "diode_model",
    "title": "光伏组件二极管模型（模型31~33）",
    "version": "1.0.0",
    "description": (
        "基于肖克莱理想二极管方程的光伏组件电学模型。"
        "单二极管模型（式56-57）仅考虑PN结复合；"
        "双二极管模型增加空间电荷区复合；"
        "三二极管模型进一步考虑缺陷复合。"
        "支持计算完整I-V曲线或指定工作点。"
    ),
    "author": "PV Team",
    "category": "光伏转换",
    "related_models": {
        "pre": ["solar_position", "perez_model", "faiman_temp_model"],
        "post": [],
        "depends_on": [],
        "conflicts_with": []
    },
    "inputs": [
        {
            "name": "gc",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "入射有效辐照度 Gc（W/m²）"
        },
        {
            "name": "t_cell",
            "type": "float",
            "required": True,
            "min": -40.0,
            "max": 100.0,
            "description": "电池温度 Tcell（°C）"
        },
        {
            "name": "voltage",
            "type": "float",
            "required": False,
            "min": 0.0,
            "default": None,
            "description": "工作电压 V（V），用于计算单点；不传则返回完整I-V曲线"
        },
        {
            "name": "model_type",
            "type": "enum",
            "required": False,
            "default": "single",
            "options": ["single", "double", "triple"],
            "description": "二极管模型类型：single（单二极管，模型31）/ double（双二极管，模型32）/ triple（三二极管，模型33）"
        },
        {
            "name": "il_ref",
            "type": "float",
            "required": False,
            "default": 5.0,
            "description": "STC下光电流 IL_ref（A）"
        },
        {
            "name": "io_ref",
            "type": "float",
            "required": False,
            "default": 1e-9,
            "description": "STC下第一反向饱和电流 I0_ref（A）"
        },
        {
            "name": "rs",
            "type": "float",
            "required": False,
            "default": 0.5,
            "description": "串联电阻 Rs（Ω）"
        },
        {
            "name": "rsh_ref",
            "type": "float",
            "required": False,
            "default": 200.0,
            "description": "STC下并联电阻 Rsh_ref（Ω）"
        },
        {
            "name": "n",
            "type": "float",
            "required": False,
            "default": 1.2,
            "description": "第一二极管理想因子 n1"
        },
        {
            "name": "ns",
            "type": "int",
            "required": False,
            "default": 60,
            "description": "串联电池数 Ns"
        },
        {
            "name": "io2_ref",
            "type": "float",
            "required": False,
            "default": 1e-7,
            "description": "第二反向饱和电流 I02_ref（A），仅 double/triple 使用"
        },
        {
            "name": "n2",
            "type": "float",
            "required": False,
            "default": 2.0,
            "description": "第二二极管理想因子 n2，仅 double/triple 使用"
        },
        {
            "name": "io3_ref",
            "type": "float",
            "required": False,
            "default": 1e-6,
            "description": "第三反向饱和电流 I03_ref（A），仅 triple 使用"
        },
        {
            "name": "n3",
            "type": "float",
            "required": False,
            "default": 3.0,
            "description": "第三二极管理想因子 n3，仅 triple 使用"
        }
    ],
    "outputs": [
        {
            "name": "current",
            "type": "float",
            "unit": "A",
            "description": "输出电流 I（A），单点计算时返回"
        },
        {
            "name": "power",
            "type": "float",
            "unit": "W",
            "description": "输出功率 P = V × I（W），单点计算时返回"
        },
        {
            "name": "iv_curve",
            "type": "list",
            "unit": "",
            "description": "完整I-V曲线点列表，每点含 voltage/current/power，电压未指定时返回"
        },
        {
            "name": "voc",
            "type": "float",
            "unit": "V",
            "description": "开路电压 Voc（V）"
        },
        {
            "name": "isc",
            "type": "float",
            "unit": "A",
            "description": "短路电流 Isc（A）"
        },
        {
            "name": "vmpp",
            "type": "float",
            "unit": "V",
            "description": "最大功率点电压 Vmpp（V）"
        },
        {
            "name": "impp",
            "type": "float",
            "unit": "A",
            "description": "最大功率点电流 Impp（A）"
        },
        {
            "name": "pmpp",
            "type": "float",
            "unit": "W",
            "description": "最大功率 Pmax（W）"
        },
        {
            "name": "ff",
            "type": "float",
            "unit": "",
            "description": "填充因子 FF = Pmax / (Voc × Isc)"
        }
    ],
    "tags": ["diode", "pv-module", "iv-curve", "single-diode", "double-diode", "triple-diode"],
    "execution": {
        "timeout": 30,
        "cacheable": True,
        "cache_ttl": 1800
    }
}
