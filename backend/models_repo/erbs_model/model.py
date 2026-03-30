def run(inputs: dict) -> dict:
    import math

    ghi          = inputs["ghi"]
    e0           = inputs["e0"]
    solar_zenith = inputs["solar_zenith"]

    # 防止除零
    if e0 <= 0 or ghi <= 0:
        return {"k": 0.0, "kt": 0.0, "dhi": 0.0, "bni": 0.0}

    # 晴空指数 kt = GHI / E0
    kt = ghi / e0
    kt = max(0.0, min(1.0, kt))

    # 散射分数 k（Erbs 分段公式）
    # 式(4): kt <= 0.22
    if kt <= 0.22:
        k = 1.0 - 0.09 * kt
    # 式(5): 0.22 < kt <= 0.80
    elif kt <= 0.80:
        k = (0.9511
             - 0.1604 * kt
             + 4.388  * kt ** 2
             - 16.638 * kt ** 3
             + 12.336 * kt ** 4)
    # 式(6): kt > 0.80
    else:
        k = 0.165

    k = max(0.0, min(1.0, k))

    # DHI = k * GHI
    dhi = k * ghi

    # BNI = (GHI - DHI) / cos(Z)
    cos_z = math.cos(math.radians(solar_zenith))
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
