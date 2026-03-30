MODEL_META = {
    "name": "faiman_temp_model",
    "title": "Faiman/PVSyst/Mattei/SAM 电池温度模型（模型28~30）",
    "version": "1.0.0",
    "description": (
        "基于热损失系数的非线性电池温度模型系列。"
        "faiman：Tmod = Tamb + Gc/(u0+u1*W)；"
        "pvsyst：在 Faiman 基础上引入组件效率和吸收系数；"
        "mattei：将光伏效率模型整合到热能平衡，考虑 Tcell 与 Pdc 相互依赖；"
        "sam：基于 NOCT 的 SAM 软件模型，支持安装方式和建筑高度调整。"
    ),
    "author": "PV Team",
    "category": "电池温度",
    "related_models": {
        "pre": ["solar_position", "perez_model"],
        "post": [],
        "depends_on": [],
        "conflicts_with": [
            "linear_temp_model",
            "king_temp_model"
        ]
    },
    "inputs": [
        {
            "name": "tamb",
            "type": "float",
            "required": True,
            "min": -50.0,
            "max": 60.0,
            "description": "环境温度 Tamb（°C）"
        },
        {
            "name": "gc",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "入射有效辐照度 Gc（W/m²）"
        },
        {
            "name": "wind_speed",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "风速 W（m/s）"
        },
        {
            "name": "model_type",
            "type": "enum",
            "required": False,
            "default": "faiman",
            "options": ["faiman", "pvsyst", "mattei", "sam"],
            "description": "模型类型：faiman / pvsyst / mattei / sam"
        },
        {
            "name": "u0",
            "type": "float",
            "required": False,
            "default": 25.0,
            "description": "热损失系数 u0（W/m²K），faiman/pvsyst 使用，典型值 25.0"
        },
        {
            "name": "u1",
            "type": "float",
            "required": False,
            "default": 6.84,
            "description": "风速热损失系数 u1（W/m²K/(m/s)），faiman/pvsyst 使用，典型值 6.84"
        },
        {
            "name": "eta_amb",
            "type": "float",
            "required": False,
            "default": 0.1,
            "description": "组件外部效率 η_amb（pvsyst 使用），典型值 0.1"
        },
        {
            "name": "alpha",
            "type": "float",
            "required": False,
            "default": 0.9,
            "description": "吸收系数 α（pvsyst 使用），典型值 0.9"
        },
        {
            "name": "eta_mpp_ref",
            "type": "float",
            "required": False,
            "default": 0.15,
            "description": "STC 下组件名义效率 η_mpp_ref（mattei 使用），典型值 0.15"
        },
        {
            "name": "gamma_pmpp",
            "type": "float",
            "required": False,
            "default": -0.004,
            "description": "最大功率温度系数 γ_pmpp（/°C，mattei 使用），典型值 -0.004"
        },
        {
            "name": "tau_alpha",
            "type": "float",
            "required": False,
            "default": 0.81,
            "description": "透射率-吸收率乘积 τα（mattei 使用），推荐值 0.81"
        },
        {
            "name": "noct",
            "type": "float",
            "required": False,
            "default": 45.0,
            "description": "名义运行电池温度 NOCT（°C，sam 使用），典型值 45.0"
        },
        {
            "name": "mounting_type",
            "type": "enum",
            "required": False,
            "default": "rack",
            "options": ["rack", "2.5_to_3.5in", "1.5_to_2.5in", "0.5_to_1.5in", "less_0.5in"],
            "description": "安装方式（sam 使用）：rack/2.5_to_3.5in/1.5_to_2.5in/0.5_to_1.5in/less_0.5in"
        },
        {
            "name": "building_height",
            "type": "enum",
            "required": False,
            "default": "low",
            "options": ["low", "high"],
            "description": "建筑高度（sam 使用）：low（一层及以下）/ high（两层及以上）"
        }
    ],
    "outputs": [
        {
            "name": "t_cell",
            "type": "float",
            "unit": "°C",
            "description": "电池/组件温度（°C）"
        },
        {
            "name": "noct_prime",
            "type": "float",
            "unit": "°C",
            "description": "调整后的 NOCT'（仅 SAM 模型输出）"
        },
        {
            "name": "wind_prime",
            "type": "float",
            "unit": "m/s",
            "description": "调整后的风速 W'（仅 SAM 模型输出）"
        }
    ],
    "tags": ["temperature", "faiman", "pvsyst", "mattei", "sam", "nonlinear"],
    "execution": {
        "timeout": 10,
        "cacheable": True,
        "cache_ttl": 1800
    }
}
