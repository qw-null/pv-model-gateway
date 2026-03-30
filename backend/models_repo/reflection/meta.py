MODEL_META = {
    "name": "reflection",
    "title": "反射损失模型",
    "version": "1.0.0",
    "description": "计算光伏组件表面的反射损失（IAM 入射角修正）",
    "author": "PV Team",
    "inputs": [
        {
            "name": "aoi",
            "type": "float",
            "required": True,
            "min": 0.0,
            "max": 90.0,
            "description": "入射角 AOI (°)"
        },
        {
            "name": "model",
            "type": "enum",
            "options": ["physical", "ashrae", "martin_ruiz"],
            "required": False,
            "default": "physical",
            "description": "IAM 模型选择"
        },
        {
            "name": "n",
            "type": "float",
            "required": False,
            "default": 1.526,
            "description": "玻璃折射率（physical 模型使用）"
        },
        {
            "name": "b",
            "type": "float",
            "required": False,
            "default": 0.05,
            "description": "ASHRAE 模型系数 b"
        },
    ],
    "outputs": [
        {"name": "iam",          "type": "float", "unit": "",  "description": "入射角修正系数 (0~1)"},
        {"name": "reflection_loss", "type": "float", "unit": "%", "description": "反射损失百分比"},
    ],
    "tags": ["reflection", "iam", "optical"],
    "execution": {"timeout": 15, "cacheable": True, "cache_ttl": 3600},
}
