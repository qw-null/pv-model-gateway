# models_repo/aoi_calculator/meta.py

MODEL_META = {
    # ── 基本信息 ──────────────────────────────────────────────
    "name":        "aoi_calculator",
    "title":       "直接辐射入射角计算模型（AOI）",
    "category":    "光学修正",
    "version":     "1.0.0",
    "description": (
        "计算太阳光线与光伏组件前表面法线之间的夹角（AOI）。"
        "基于天文与几何公式，依赖太阳高度角、太阳方位角、"
        "组件倾斜角和组件方位角四个参数进行计算。"
    ),
    "author": "系统架构组",

    # ── 输入参数 ──────────────────────────────────────────────
    "inputs": [
        {
            "name":        "alpha",
            "type":        "float",
            "required":    True,
            "description": "太阳高度角 α，太阳相对于水平面的仰角",
            "unit":        "°",
        },
        {
            "name":        "gamma_s",
            "type":        "float",
            "required":    True,
            "description": "太阳方位角 γs，由地理纬度、日期和时刻计算得出",
            "unit":        "°",
        },
        {
            "name":        "beta",
            "type":        "float",
            "required":    True,
            "description": "组件倾斜角 β，组件平面与水平面的夹角",
            "unit":        "°",
        },
        {
            "name":        "gamma_c",
            "type":        "float",
            "required":    True,
            "description": "组件方位角 γc，组件朝向的方位角（正南为180°，正北为0°/360°）",
            "unit":        "°",
        },
    ],

    # ── 输出参数 ──────────────────────────────────────────────
    "outputs": [
        {
            "name":        "AOI",
            "type":        "float",
            "description": "AOI（直接辐射入射角，太阳光线与组件法线的夹角）",
            "unit":        "°",
        },
        {
            "name":        "cos_AOI",
            "type":        "float",
            "description": "入射角余弦值 cos(AOI)，可直接用于辐照度投影计算",
            "unit":        "",
        },
    ],

    # ── 执行配置 ──────────────────────────────────────────────
    "execution": {
        "timeout_ms": 3000,
        "async":      False,
    },
}
