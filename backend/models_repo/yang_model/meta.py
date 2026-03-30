# Yang5 各 Cluster 系数表（供描述参考）
_YANG5_CLUSTERS = {
    1: (0.13105, -4.36740, 7.68051,  0.00540,  0.01748,  0.91590, 0.52176, -1.68819),
    2: (-0.01014,-3.33038, 5.72327,  0.01296,  0.01230, -0.96483, 0.94204, -1.68332),
    3: (-0.27475, 0.36085, 0.39860,  0.00479,  0.00039,-10.20264, 2.12475, -1.78455),
    4: (-0.01095,-0.92129, 3.65015,  0.00767,  0.00494, -3.76465, 1.36482, -2.11867),
    5: (0.04297, -1.64437, 4.71808,  0.01462,  0.00745, -3.35223, 1.25192, -2.36477),
}

MODEL_META = {
    "name": "yang_model",
    "title": "Yang 分离模型（模型6~10）",
    "version": "1.0.0",
    "description": (
        "杨大智在 Engerer2 基础上提出的五种改进分离模型。"
        "Yang1/2 引入卫星漫射分数 k_s；"
        "Yang3/4 用小时级 Engerer2 估计替代 k_s；"
        "Yang5 采用动态气候分区系数（5类气候区），具有准通用性。"
    ),
    "author": "PV Team",
    "inputs": [
        {
            "name": "kt",
            "type": "float",
            "required": True,
            "min": 0.0,
            "max": 1.0,
            "description": "晴空指数 kt = GHI / E0"
        },
        {
            "name": "ast",
            "type": "float",
            "required": True,
            "min": 0.0,
            "max": 24.0,
            "description": "视太阳时 AST (小时，0~24)"
        },
        {
            "name": "solar_zenith",
            "type": "float",
            "required": True,
            "min": 0.0,
            "max": 90.0,
            "description": "太阳天顶角 Z (°)"
        },
        {
            "name": "ktc",
            "type": "float",
            "required": True,
            "min": 0.0,
            "max": 1.0,
            "description": "晴空模型估算的晴空指数 ktc"
        },
        {
            "name": "ghi",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "水平面总辐照度 GHI (W/m²)"
        },
        {
            "name": "ghc",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "晴空 GHI 估算值 Ghc (W/m²)"
        },
        {
            "name": "k_ext",
            "type": "float",
            "required": True,
            "min": 0.0,
            "max": 1.0,
            "description": (
                "外部辅助输入：Yang1/2 传入卫星漫射分数 k_s；"
                "Yang3/4/5 传入小时级 Engerer2 估计值 k_hourly"
            )
        },
        {
            "name": "model_type",
            "type": "enum",
            "options": ["yang1", "yang2", "yang3", "yang4", "yang5"],
            "required": False,
            "default": "yang4",
            "description": "模型类型选择"
        },
        {
            "name": "cluster",
            "type": "int",
            "required": False,
            "default": 1,
            "min": 1,
            "max": 5,
            "description": "气候分区编号 1~5（仅 Yang5 使用，需根据站点气候类型选择）"
        },
    ],
    "outputs": [
        {"name": "k",   "type": "float", "unit": "",     "description": "散射分数 k = DHI / GHI"},
        {"name": "dhi", "type": "float", "unit": "W/m²", "description": "漫射水平辐照度 DHI"},
        {"name": "bni", "type": "float", "unit": "W/m²", "description": "光束法向辐照度 BNI"},
    ],
    "tags": ["irradiance", "separation", "yang"],
    "execution": {"timeout": 10, "cacheable": True, "cache_ttl": 1800},
}
