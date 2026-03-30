def run(inputs: dict) -> dict:
    import pvlib
    import pandas as pd
    import math

    lat    = inputs["latitude"]
    lon    = inputs["longitude"]
    dt_str = inputs["datetime"]
    tz     = inputs.get("timezone", "Asia/Shanghai")

    # 入参保护：datetime 不能为空
    if not dt_str or str(dt_str).strip() == "":
        raise ValueError(
            "datetime 参数不能为空，请传入 ISO 格式时间，如 2024-06-21T12:00:00"
        )

    # 时间解析
    try:
        times = pd.DatetimeIndex([pd.Timestamp(dt_str, tz=tz)])
    except Exception:
        raise ValueError(
            f"datetime 格式不正确: '{dt_str}'，请使用 ISO 格式，如 2024-06-21T12:00:00"
        )

    # 计算太阳位置
    location  = pvlib.location.Location(lat, lon, tz=tz)
    solar_pos = location.get_solarposition(times)

    altitude = float(solar_pos["elevation"].iloc[0])
    azimuth  = float(solar_pos["azimuth"].iloc[0])
    zenith   = float(solar_pos["apparent_zenith"].iloc[0])

    # 模型层兜底：NaN/Inf 替换为 0
    def safe(v):
        return 0.0 if math.isnan(v) or math.isinf(v) else round(v, 4)

    return {
        "altitude":   safe(altitude),
        "azimuth":    safe(azimuth),
        "zenith":     safe(zenith),
        "is_daytime": safe(altitude) > 0,
    }
