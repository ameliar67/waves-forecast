def surf_quality_rating(
    wave_height,
    swell_period,
    wind_speed,
):

    # Returns: 'Poor', 'Fair', 'Good', or 'Epic'
    # Score from 0 to 6
    score = (
        score_wave_height(wave_height)
        + score_swell_period(swell_period)
        + score_wind_speed(wind_speed)
    )

    if score >= 7:
        return "Epic"
    elif score >= 5:
        return "Good"
    elif score >= 3:
        return "Fair"
    else:
        return "Poor"


def score_wave_height(height_ft):
    if height_ft < 1.5:
        return 0
    elif height_ft <= 4.5:
        return 2  # ideal size
    elif height_ft <= 7:
        return 1  # big but still surfable
    else:
        return 0  # too heavy for most


def score_swell_period(period_s):
    if period_s < 8:
        return 0  # weak wind swell
    elif period_s < 11:
        return 1  # decent swell
    else:
        return 2  # clean groundswell


def score_wind_speed(knots):
    if knots <= 6:
        return 2  # glassy
    elif knots <= 12:
        return 1  # light wind
    else:
        return 0  # choppy or blown out
