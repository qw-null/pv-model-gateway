import math

D2R = math.pi / 180.0


def _erbs_separation(ghi, etr, solar_zenith_deg):
    cos_z = math.cos(solar_zenith_deg * D2R)
    if cos_z <= 0 or etr <= 0:
        return 0.0
    kt = ghi / (etr * cos_z)
    kt = min(kt, 1.0)
    if kt <= 0.22:
        df = 1.0 - 0.09 * kt
    elif kt <= 0.80:
        df = (0.9511
              - 0.1604 * kt
              + 4.388  * math.pow(kt, 2)
              - 16.638 * math.pow(kt, 3)
              + 12.336 * math.pow(kt, 4))
    else:
        df = 0.165
    return max(0.0, df * ghi)


def _beam_tilt_ratio(tilt_deg, azimuth_deg, solar_zenith_deg,
                     declination_deg, latitude_deg, hour_angle_deg):
    b   = tilt_deg         * D2R
    g   = azimuth_deg      * D2R
    z   = solar_zenith_deg * D2R
    d   = declination_deg  * D2R
    phi = latitude_deg     * D2R
    w   = hour_angle_deg   * D2R
    cos_z = math.cos(z)
    if cos_z <= 1e-6:
        return 0.0
    if abs(azimuth_deg) < 1e-6:
        cos_theta_i = (math.cos(d) * math.cos(w) * math.cos(phi - b)
                       + math.sin(d) * math.sin(phi - b))
    else:
        cos_theta_i = (
            math.cos(d) * math.cos(w) * (
                math.cos(phi) * math.cos(b)
                + math.sin(phi) * math.sin(b) * math.cos(g)
            )
            + math.cos(d) * math.sin(w) * math.sin(b) * math.sin(g)
            + math.sin(d) * (
                math.sin(phi) * math.cos(b)
                - math.cos(phi) * math.sin(b) * math.cos(g)
            )
        )
    rb = max(0.0, cos_theta_i) / cos_z
    return rb


def _crossed_string_vf(emit_len, recv_len, d_cross1, d_cross2):
    if emit_len <= 0:
        return 0.0
    non_cross = emit_len + recv_len
    cross_sum = d_cross1 + d_cross2
    return max(0.0, (cross_sum - non_cross) / (2.0 * emit_len))


def _view_factors_front(tilt_deg, module_height, row_spacing,
                         ground_clearance, multi_row):
    b  = tilt_deg * D2R
    H  = module_height
    M  = row_spacing
    h0 = ground_clearance
    vf_sky_basic = (1.0 + math.cos(b)) / 2.0
    vf_gnd_basic = (1.0 - math.cos(b)) / 2.0
    if not multi_row:
        return {
            "vf_sky":       vf_sky_basic,
            "vf_shd_gnd":   0.0,
            "vf_unshd_gnd": vf_gnd_basic,
            "vf_rear_row":  0.0
        }
    h_top = h0 + H * math.sin(b)
    x_top = H  * math.cos(b)
    x_bot = 0.0
    x_next_bot = M
    x_next_top = M + H * math.cos(b)
    h_next_bot = h0
    h_next_top = h0 + H * math.sin(b)
    shadow_len = (h_top / math.tan(b) if math.sin(b) > 1e-6 else 0.0)
    shadow_len = min(shadow_len, M)
    if shadow_len > 1e-9:
        d1 = math.sqrt(math.pow(x_top - 0.0, 2)       + math.pow(h_top - 0.0, 2))
        d2 = math.sqrt(math.pow(x_bot - shadow_len, 2) + math.pow(h0   - 0.0, 2))
        vf_shd = _crossed_string_vf(H, shadow_len, d1, d2)
    else:
        vf_shd = 0.0
    d1_row = math.sqrt(math.pow(x_top - x_next_bot, 2) + math.pow(h_top - h_next_bot, 2))
    d2_row = math.sqrt(math.pow(x_bot - x_next_top, 2) + math.pow(h0   - h_next_top, 2))
    vf_rear_row = _crossed_string_vf(H, H, d1_row, d2_row)
    vf_unshd = vf_gnd_basic - vf_shd
    vf_sky   = vf_sky_basic - vf_rear_row
    return {
        "vf_sky":       max(0.0, vf_sky),
        "vf_shd_gnd":   max(0.0, vf_shd),
        "vf_unshd_gnd": max(0.0, vf_unshd),
        "vf_rear_row":  max(0.0, vf_rear_row)
    }


def _view_factors_rear(tilt_deg, module_height, row_spacing,
                        ground_clearance, multi_row):
    b  = tilt_deg * D2R
    H  = module_height
    M  = row_spacing
    h0 = ground_clearance
    vf_sky_back = (1.0 - math.cos(b)) / 2.0
    vf_gnd_back = (1.0 + math.cos(b)) / 2.0
    if not multi_row:
        return {
            "vf_sky":       vf_sky_back,
            "vf_shd_gnd":   0.0,
            "vf_unshd_gnd": vf_gnd_back,
            "vf_rear_row":  0.0
        }
    h_top = h0 + H * math.sin(b)
    x_top = H  * math.cos(b)
    shadow_len = (h_top / math.tan(b) if math.sin(b) > 1e-6 else 0.0)
    shadow_len = min(shadow_len, M)
    if shadow_len > 1e-9:
        d1 = math.sqrt(math.pow(x_top,      2) + math.pow(h_top, 2))
        d2 = math.sqrt(math.pow(shadow_len, 2) + math.pow(h0,    2))
        vf_shd = _crossed_string_vf(H, shadow_len, d1, d2)
    else:
        vf_shd = 0.0
    x_next_bot = M
    x_next_top = M + H * math.cos(b)
    h_next_top = h0 + H * math.sin(b)
    d1_row = math.sqrt(math.pow(x_top - x_next_top, 2) + math.pow(h_top - h_next_top, 2))
    d2_row = math.sqrt(math.pow(0.0   - x_next_bot, 2) + math.pow(h0   - h0,         2))
    vf_rear_row = _crossed_string_vf(H, H, d1_row, d2_row)
    vf_unshd = vf_gnd_back - vf_shd - vf_rear_row
    return {
        "vf_sky":       max(0.0, vf_sky_back),
        "vf_shd_gnd":   max(0.0, vf_shd),
        "vf_unshd_gnd": max(0.0, vf_unshd),
        "vf_rear_row":  max(0.0, vf_rear_row)
    }


def _compute_irradiance(ghi, dhi, rb, vf, albedo_ground, albedo_module):
    dni = max(0.0, ghi - dhi)
    g_beam      = dni * rb
    g_diffuse   = dhi * vf["vf_sky"]
    g_reflected = (
        ghi * albedo_ground * (vf["vf_shd_gnd"] + vf["vf_unshd_gnd"])
        + ghi * albedo_module * vf["vf_rear_row"]
    )
    g_total = g_beam + g_diffuse + g_reflected
    return {
        "g_beam":      round(max(0.0, g_beam),      4),
        "g_diffuse":   round(max(0.0, g_diffuse),   4),
        "g_reflected": round(max(0.0, g_reflected), 4),
        "g_total":     round(max(0.0, g_total),     4)
    }


def run(inputs):
    mode             = inputs.get("mode", "bifacial_multi")
    ghi              = float(inputs["ghi"])
    etr              = float(inputs.get("etr", 1367.0))
    solar_zenith     = float(inputs["solar_zenith"])
    solar_azimuth    = float(inputs["solar_azimuth"])
    declination      = float(inputs["declination"])
    latitude         = float(inputs["latitude"])
    hour_angle       = float(inputs["hour_angle"])
    tilt             = float(inputs["tilt"])
    azimuth          = float(inputs.get("azimuth", 0.0))
    module_height    = float(inputs.get("module_height", 2.0))
    row_spacing      = float(inputs.get("row_spacing", 5.0))
    ground_clearance = float(inputs.get("ground_clearance", 0.5))
    albedo_ground    = float(inputs.get("albedo_ground", 0.2))
    albedo_module    = float(inputs.get("albedo_module", 0.03))
    eta_front        = float(inputs.get("eta_front", 0.21))
    eta_rear         = float(inputs.get("eta_rear", 0.18))
    module_area      = float(inputs.get("module_area", 2.0))

    valid_modes = {"monofacial_single", "monofacial_multi",
                   "bifacial_single",   "bifacial_multi"}
    if mode not in valid_modes:
        raise ValueError("invalid mode: " + mode)
    if ghi < 0:
        raise ValueError("ghi < 0")
    if not (0.0 <= tilt <= 90.0):
        raise ValueError("tilt out of range")
    if module_area <= 0:
        raise ValueError("module_area must be > 0")

    is_bifacial  = mode.startswith("bifacial")
    is_multi_row = mode.endswith("multi")

    if inputs.get("dhi") is not None:
        dhi = float(inputs["dhi"])
    else:
        dhi = _erbs_separation(ghi, etr, solar_zenith)
    dhi = max(0.0, min(dhi, ghi))

    rb_front = _beam_tilt_ratio(
        tilt, azimuth,
        solar_zenith, declination, latitude, hour_angle
    )
    vf_front = _view_factors_front(
        tilt, module_height, row_spacing,
        ground_clearance, is_multi_row
    )
    front = _compute_irradiance(
        ghi, dhi, rb_front, vf_front, albedo_ground, albedo_module
    )

    result = {
        "vf_front_sky":      round(vf_front["vf_sky"], 6),
        "vf_front_ground":   round(vf_front["vf_shd_gnd"] + vf_front["vf_unshd_gnd"], 6),
        "g_front":           front["g_total"],
        "g_front_beam":      front["g_beam"],
        "g_front_diffuse":   front["g_diffuse"],
        "g_front_reflected": front["g_reflected"],
        "vf_rear_sky":       0.0,
        "vf_rear_ground":    0.0,
        "g_rear":            0.0,
        "g_rear_beam":       0.0,
        "g_rear_diffuse":    0.0,
        "g_rear_reflected":  0.0,
    }

    if is_bifacial:
        rear_tilt    = 180.0 - tilt
        rear_azimuth = (azimuth + 180.0) if azimuth <= 0.0 else (azimuth - 180.0)
        rb_rear = _beam_tilt_ratio(
            rear_tilt, rear_azimuth,
            solar_zenith, declination, latitude, hour_angle
        )
        vf_rear = _view_factors_rear(
            tilt, module_height, row_spacing,
            ground_clearance, is_multi_row
        )
        rear = _compute_irradiance(
            ghi, dhi, rb_rear, vf_rear, albedo_ground, albedo_module
        )
        result.update({
            "vf_rear_sky":      round(vf_rear["vf_sky"], 6),
            "vf_rear_ground":   round(vf_rear["vf_shd_gnd"] + vf_rear["vf_unshd_gnd"], 6),
            "g_rear":           rear["g_total"],
            "g_rear_beam":      rear["g_beam"],
            "g_rear_diffuse":   rear["g_diffuse"],
            "g_rear_reflected": rear["g_reflected"],
        })

    g_front_val   = result["g_front"]
    g_rear_val    = result["g_rear"]
    g_total       = g_front_val + g_rear_val
    power_density = eta_front * g_front_val + eta_rear * g_rear_val
    power_total   = power_density * module_area

    result.update({
        "g_total":       round(g_total,       4),
        "power_density": round(power_density, 4),
        "power_total":   round(power_total,   4),
    })

    return result
