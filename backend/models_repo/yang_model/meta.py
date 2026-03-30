MODEL_META = {
    "name": "yang_model",
    "title": "Yang 分离模型（模型6~10）",
    "version": "1.0.0",
    "description": (
        "杨大智在 Engerer2 基础上提出的五种直散分离模型。"
        "Yang1/2 引入卫星衍生漫射分数 k_s；"
        "Yang3/4 用小时级 Engerer2 估计代替 k_s；"
        "Yang5 在 Yang4 基础上引入辐射气候分区动态系数，具有准通用性。"
    ),
    "author": "PV Team",
    "category": "辐照分离",
    "related_models": {
        "pre": ["solar_position", "engerer_model"],
        "post": [],
        "depends_on": [],
        "conflicts_with": []
    },
    "inputs": [
        {
            "name": "kt",
            "type": "float",
            "required": True,
            "min": 0.0,
            "max": 1.2,
            "description": "晴空指数 kt = GHI / E0"
        },
        {
            "name": "ast",
            "type": "float",
            "required": True,
            "min": 0.0,
            "max": 24.0,
            "description": "视太阳时 AST（小时，0~24）"
        },
        {
            "name": "solar_zenith",
            "type": "float",
            "required": True,
            "min": 0.0,
            "max": 90.0,
            "description": "太阳天顶角 Z（°）"
        },
        {
            "name": "ktc",
            "type": "float",
            "required": True,
            "min": 0.0,
            "max": 1.2,
            "description": "晴空模型估算的晴空指数 ktc"
        },
        {
            "name": "ghi",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "水平面总辐照度 GHI（W/m²）"
        },
        {
            "name": "ghc",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "晴空 GHI 估算值 Ghc（W/m²），用于计算云增强项 kde"
        },
        {
            "name": "k_s",
            "type": "float",
            "required": False,
            "min": 0.0,
            "max": 1.0,
            "default": 0.0,
            "description": "卫星衍生漫射分数 k^(s)（Yang1/Yang2 必填，Yang3/4/5 不需要）"
        },
        {
            "name": "k_hourly_engerer2",
            "type": "float",
            "required": False,
            "min": 0.0,
            "max": 1.0,
            "default": 0.0,
            "description": "小时级 Engerer2 散射分数估计值（Yang3/4/5 必填，Yang1/2 不需要）"
        },
        {
            "name": "cluster",
            "type": "enum",
            "required": False,
            "default": "1",
            "options": ["1", "2", "3", "4", "5"],
            "description": "辐射气候分区编号（仅 Yang5 使用，对应表2系数）"
        },
        {
            "name": "model_type",
            "type": "enum",
            "required": False,
            "default": "yang4",
            "options": ["yang1", "yang2", "yang3", "yang4", "yang5"],
            "description": "模型类型：yang1~yang5，默认 yang4"
        }
    ],
    "outputs": [
        {
            "name": "k",
            "type": "float",
            "unit": "",
            "description": "散射分数 k = DHI / GHI"
        },
        {
            "name": "dhi",
            "type": "float",
            "unit": "W/m²",
            "description": "漫射水平辐照度 DHI"
        },
        {
            "name": "bni",
            "type": "float",
            "unit": "W/m²",
            "description": "光束法向辐照度 BNI = (GHI - DHI) / cos(Z)"
        },
        {
            "name": "k_de",
            "type": "float",
            "unit": "",
            "description": "云增强漫射比例 kde = max(0, 1 - Ghc/Ghi)"
        }
    ],
    "tags": ["yang", "irradiance", "separation", "satellite"],
    "execution": {
        "timeout": 10,
        "cacheable": True,
        "cache_ttl": 1800
    }
}
