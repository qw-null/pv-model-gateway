def run(inputs: dict) -> dict:
    import pvlib

    aoi   = inputs["aoi"]
    model = inputs.get("model", "physical")
    n     = inputs.get("n", 1.526)
    b     = inputs.get("b", 0.05)

    if model == "physical":
        iam = pvlib.iam.physical(aoi, n=n)
    elif model == "ashrae":
        iam = pvlib.iam.ashrae(aoi, b=b)
    elif model == "martin_ruiz":
        iam = pvlib.iam.martin_ruiz(aoi)
    else:
        raise ValueError(f"不支持的 IAM 模型: {model}")

    iam = float(iam)
    return {
        "iam":             round(max(0.0, min(1.0, iam)), 6),
        "reflection_loss": round((1 - iam) * 100, 4),
    }
