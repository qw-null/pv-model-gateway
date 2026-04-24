def run(inputs: dict) -> dict:
    import math

    ghi          = inputs["ghi"]
    e0           = inputs["e0"]          # 地外法向辐射 (W/m²)
    solar_zenith = inputs["solar_zenith"]

    cos_z = math.cos(math.radians(solar_zenith))

    # 地外水平辐射
    eth = e0 * cos_z

    # 防止除零（e0、ghi 或 eth 无效时直接返回）
    if e0 <= 0 or ghi <= 0 or eth <= 0.01:
        return {"k": 0.0, "kt": 0.0, "dhi": 0.0, "bni": 0.0}

    # 晴空指数 kt = GHI / ETH  ← 修正点
    kt = ghi / eth
    kt = max(0.0, min(1.0, kt))

    # Erbs 散射分数
    if kt <= 0.22:
        k = 1.0 - 0.09 * kt
    elif kt <= 0.80:
        k = (0.9511
             - 0.1604 * kt
             + 4.388  * kt ** 2
             - 16.638 * kt ** 3
             + 12.336 * kt ** 4)
    else:
        k = 0.165

    k = max(0.0, min(1.0, k))

    dhi = k * ghi

    if cos_z > 0.01:
        bni = (ghi - dhi) / cos_z
    else:
        bni = 0.0

    return {
        "k":   round(k,   6),
        "kt":  round(kt,  6),
        "dhi": round(max(0.0, dhi), 4),
        "bni": round(max(0.0, bni), 4),
    }
