MODEL_META = {
    "id": 3,
    "name": "erbs_model",
    "title": "Erbs 分离模型（模型2）",
    "version": "1.0.0",
    "description": (
        "Erbs 等人基于美国北纬31°~42°五个站点数据提出的分离模型，"
        "通过晴空指数 kt 估算散射分数 k，进而计算 DHI 和 BNI。"
        "PVsyst 软件中采用了该模型。"
    ),
    "author": "PV Team",
    "category": "辐照分离",
    "inputs": [
        {
            "name": "ghi",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "水平面总辐照度 GHI (W/m²)"
        },
        {
            "name": "e0",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "外层空间水平面辐照度 E0 (W/m²)"
        },
        {
            "name": "solar_zenith",
            "type": "float",
            "required": True,
            "min": 0.0,
            "max": 90.0,
            "description": "太阳天顶角 Z (°)"
        },
    ],
    "outputs": [
        {"name": "k",   "type": "float", "unit": "",     "description": "散射分数 k = DHI / GHI"},
        {"name": "kt",  "type": "float", "unit": "",     "description": "晴空指数 kt = GHI / E0"},
        {"name": "dhi", "type": "float", "unit": "W/m²", "description": "漫射水平辐照度 DHI"},
        {"name": "bni", "type": "float", "unit": "W/m²", "description": "光束法向辐照度 BNI"},
    ],
    "tags": ["irradiance", "separation", "erbs"],
    "execution": {"timeout": 10, "cacheable": True, "cache_ttl": 1800},
}
