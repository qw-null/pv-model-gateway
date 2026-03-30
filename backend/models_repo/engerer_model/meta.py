MODEL_META = {
    "name": "engerer_model",
    "title": "Engerer 分离模型（模型3~5）",
    "version": "1.0.0",
    "description": (
        "Engerer 提出的三种分离模型：Engerer1（非云增强条件）、"
        "Engerer2（全天空条件，增加云增强线性校正项）、"
        "Engerer3（晴天条件优化系数）。"
        "基于 S 型逻辑函数，引入视太阳时 AST、天顶角 Z 和晴空偏差 Δktc。"
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
            "name": "solar_zenith",
            "type": "float",
            "required": True,
            "min": 0.0,
            "max": 90.0,
            "description": "太阳天顶角 Z (°)"
        },
        {
            "name": "model_type",
            "type": "enum",
            "options": ["engerer1", "engerer2", "engerer3"],
            "required": False,
            "default": "engerer2",
            "description": "模型类型选择：engerer1/engerer2/engerer3"
        },
    ],
    "outputs": [
        {"name": "k",    "type": "float", "unit": "",     "description": "散射分数 k = DHI / GHI"},
        {"name": "dhi",  "type": "float", "unit": "W/m²", "description": "漫射水平辐照度 DHI"},
        {"name": "bni",  "type": "float", "unit": "W/m²", "description": "光束法向辐照度 BNI"},
        {"name": "k_de", "type": "float", "unit": "",     "description": "云增强漫射比例 kde（仅 Engerer2 有效）"},
    ],
    "tags": ["irradiance", "separation", "engerer"],
    "execution": {"timeout": 10, "cacheable": True, "cache_ttl": 1800},
}
