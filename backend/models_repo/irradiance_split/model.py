def run(inputs: dict) -> dict:
    import pvlib
    import pandas as pd

    ghi          = inputs["ghi"]
    solar_zenith = inputs["solar_zenith"]
    dt_str       = inputs["datetime"]
    method       = inputs.get("method", "erbs")

    times = pd.DatetimeIndex([pd.Timestamp(dt_str)])

    if method == "erbs":
        result = pvlib.irradiance.erbs(ghi, solar_zenith, times)
        dni = float(result["dni"].iloc[0])
        dhi = float(result["dhi"].iloc[0])
        kt  = float(result["kt"].iloc[0])
    elif method == "boland":
        result = pvlib.irradiance.boland(ghi, solar_zenith, times)
        dni = float(result["dni"].iloc[0])
        dhi = float(result["dhi"].iloc[0])
        kt  = float(result["kt"].iloc[0])
    elif method == "disc":
        result = pvlib.irradiance.disc(ghi, solar_zenith, times)
        dni = float(result["dni"].iloc[0])
        dhi = max(0.0, ghi - dni * max(0, __import__("math").cos(
            __import__("math").radians(solar_zenith))))
        kt  = float(result["kt"].iloc[0])
    else:
        raise ValueError(f"不支持的分离方法: {method}")

    return {
        "dni": round(max(0.0, dni), 4),
        "dhi": round(max(0.0, dhi), 4),
        "kt":  round(max(0.0, kt),  4),
    }
