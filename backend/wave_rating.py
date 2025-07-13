def surf_quality_rating(
    wave_height: int, swell_period: int, wind_speed: int, tide_level: int
) -> str:  # in meters
    """
    Returns: 'Poor', 'Fair', 'Good', or 'Epic'
    Score range: 0 to 8 (if each component scores up to 2)
    """

    score = (
        score_wave_height(wave_height)
        + score_swell_period(swell_period)
        + score_wind_speed(wind_speed)
        + score_tide_level(tide_level)
    )

    if score >= 7:
        return "Epic"
    elif score >= 5:
        return "Good"
    elif score >= 3:
        return "Fair"
    else:
        return "Poor"


def score_tide_level(normalized_tide):
    if 0.4 <= normalized_tide <= 0.6:
        return 2  # Mid-tide sweet spot
    elif 0.25 <= normalized_tide < 0.4 or 0.6 < normalized_tide <= 0.75:
        return 1  # Acceptable
    else:
        return 0  # Too high or too low


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
