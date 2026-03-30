MODEL_META = {
    "name": "bifacial_irradiance",
    "title": "双面光伏组件斜面总辐照度模型（式70~89）",
    "version": "1.0.0",
    "description": (
        "基于 Hottel Crossed String 规则计算视角因数，"
        "分别计算双面光伏组件前表面（式70~78）和背面（式79~87）接收到的"
        "散射、直射、反射三类辐照度分量，汇总得到前/背面总辐照度（式76/86/87），"
        "进而计算双面组件总辐照度（式88）和总输出功率（式89）。"
        "散射分离采用 Erbs 模型，直射转换采用 Steven-Unsworth（1979）模型。"
        "支持单面/双面、单排/多排四种组合场景。"
    ),
    "author": "PV Team",
    "category": "辐照度",
    "related_models": {
        "pre": ["solar_position", "erbs_separation"],
        "post": ["diode_model", "faiman_temp_model"],
        "depends_on": [],
        "conflicts_with": []
    },
    "inputs": [
        # ── 场景控制 ──────────────────────────────────────────
        {
            "name": "mode",
            "type": "enum",
            "required": False,
            "default": "bifacial_multi",
            "options": ["monofacial_single", "monofacial_multi",
                        "bifacial_single", "bifacial_multi"],
            "description": (
                "计算场景：monofacial_single（单面单排）、monofacial_multi（单面多排）、"
                "bifacial_single（双面单排）、bifacial_multi（双面多排）"
            )
        },
        # ── 天文/气象输入 ─────────────────────────────────────
        {
            "name": "ghi",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "水平面总辐照度 GHI（W/m²）"
        },
        {
            "name": "dhi",
            "type": "float",
            "required": False,
            "min": 0.0,
            "description": "水平面散射辐照度 DHI（W/m²）；不传则由 Erbs 模型从 GHI/ETR 分离"
        },
        {
            "name": "etr",
            "type": "float",
            "required": False,
            "min": 0.0,
            "default": 1367.0,
            "description": "大气层外水平辐照度 ETR（W/m²），用于 Erbs 分离，默认 1367"
        },
        {
            "name": "solar_zenith",
            "type": "float",
            "required": True,
            "min": 0.0,
            "max": 90.0,
            "description": "太阳天顶角 θz（°）"
        },
        {
            "name": "solar_azimuth",
            "type": "float",
            "required": True,
            "min": -180.0,
            "max": 180.0,
            "description": "太阳方位角 γs（°），正南为 0，东负西正"
        },
        {
            "name": "declination",
            "type": "float",
            "required": True,
            "min": -23.45,
            "max": 23.45,
            "description": "赤纬角 δ（°）"
        },
        {
            "name": "latitude",
            "type": "float",
            "required": True,
            "min": -90.0,
            "max": 90.0,
            "description": "当地纬度 φ（°）"
        },
        {
            "name": "hour_angle",
            "type": "float",
            "required": True,
            "min": -180.0,
            "max": 180.0,
            "description": "时角 ω（°），正午为 0，上午负，下午正"
        },
        # ── 组件几何参数 ──────────────────────────────────────
        {
            "name": "tilt",
            "type": "float",
            "required": True,
            "min": 0.0,
            "max": 90.0,
            "description": "组件倾角 β（°），水平为 0，垂直为 90"
        },
        {
            "name": "azimuth",
            "type": "float",
            "required": False,
            "default": 0.0,
            "min": -180.0,
            "max": 180.0,
            "description": "组件方位角 γ（°），正南为 0；默认 0（正南）"
        },
        {
            "name": "module_height",
            "type": "float",
            "required": False,
            "default": 2.0,
            "min": 0.1,
            "description": "组件沿斜面方向高度 H（m），默认 2.0"
        },
        {
            "name": "row_spacing",
            "type": "float",
            "required": False,
            "default": 5.0,
            "min": 0.1,
            "description": "相邻组件行间距 M（m，水平投影），多排场景使用，默认 5.0"
        },
        {
            "name": "ground_clearance",
            "type": "float",
            "required": False,
            "default": 0.5,
            "min": 0.0,
            "description": "组件下边缘离地高度（m），默认 0.5"
        },
        # ── 光学参数 ──────────────────────────────────────────
        {
            "name": "albedo_ground",
            "type": "float",
            "required": False,
            "default": 0.2,
            "min": 0.0,
            "max": 1.0,
            "description": "地面反照率 ρg，默认 0.2（草地/土壤）"
        },
        {
            "name": "albedo_module",
            "type": "float",
            "required": False,
            "default": 0.03,
            "min": 0.0,
            "max": 1.0,
            "description": "后排组件反照率 ρm（仅多排场景使用），默认 0.03"
        },
        # ── 双面效率参数（式89） ──────────────────────────────
        {
            "name": "eta_front",
            "type": "float",
            "required": False,
            "default": 0.21,
            "min": 0.0,
            "max": 1.0,
            "description": "前表面转换效率 η_front，默认 0.21"
        },
        {
            "name": "eta_rear",
            "type": "float",
            "required": False,
            "default": 0.18,
            "min": 0.0,
            "max": 1.0,
            "description": "后表面转换效率 η_rear，默认 0.18（双面率约 0.85）"
        },
        {
            "name": "module_area",
            "type": "float",
            "required": False,
            "default": 2.0,
            "min": 0.0,
            "description": "单块组件面积 A（m²），用于功率计算，默认 2.0"
        }
    ],
    "outputs": [
        {
            "name": "vf_front_sky",
            "type": "float",
            "unit": "",
            "description": "前表面对天空的视角因数 F_front_sky"
        },
        {
            "name": "vf_front_ground",
            "type": "float",
            "unit": "",
            "description": "前表面对地面（含阴影/无阴影）的视角因数 F_front_gnd"
        },
        {
            "name": "g_front",
            "type": "float",
            "unit": "W/m²",
            "description": "前表面总辐照度 G_front（W/m²）"
        },
        {
            "name": "g_front_beam",
            "type": "float",
            "unit": "W/m²",
            "description": "前表面直射分量 G_front_b（W/m²）"
        },
        {
            "name": "g_front_diffuse",
            "type": "float",
            "unit": "W/m²",
            "description": "前表面散射分量 G_front_d（W/m²）"
        },
        {
            "name": "g_front_reflected",
            "type": "float",
            "unit": "W/m²",
            "description": "前表面反射分量 G_front_r（W/m²）"
        },
        {
            "name": "vf_rear_sky",
            "type": "float",
            "unit": "",
            "description": "背面对天空的视角因数 F_rear_sky（双面模式）"
        },
        {
            "name": "vf_rear_ground",
            "type": "float",
            "unit": "",
            "description": "背面对地面的视角因数 F_rear_gnd（双面模式）"
        },
        {
            "name": "g_rear",
            "type": "float",
            "unit": "W/m²",
            "description": "背面总辐照度 G_rear（W/m²），双面模式返回"
        },
        {
            "name": "g_rear_beam",
            "type": "float",
            "unit": "W/m²",
            "description": "背面直射分量 G_rear_b（W/m²）"
        },
        {
            "name": "g_rear_diffuse",
            "type": "float",
            "unit": "W/m²",
            "description": "背面散射分量 G_rear_d（W/m²）"
        },
        {
            "name": "g_rear_reflected",
            "type": "float",
            "unit": "W/m²",
            "description": "背面反射分量 G_rear_r（W/m²）"
        },
        {
            "name": "g_total",
            "type": "float",
            "unit": "W/m²",
            "description": "双面组件总辐照度 G = G_front + G_rear（式88，W/m²）"
        },
        {
            "name": "power_density",
            "type": "float",
            "unit": "W/m²",
            "description": "单位面积总输出功率密度（式89，W/m²）"
        },
        {
            "name": "power_total",
            "type": "float",
            "unit": "W",
            "description": "单块组件总输出功率 P = power_density × A（W）"
        }
    ],
    "tags": ["bifacial", "irradiance", "view-factor", "hottel", "steven-unsworth"],
    "execution": {
        "timeout": 15,
        "cacheable": True,
        "cache_ttl": 1800
    }
}
