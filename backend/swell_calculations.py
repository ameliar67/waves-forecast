import logging
import math
from typing import cast

import surfpy


def classify_wind_relative_to_beach(wind_dir, beach_angle):
    """
    Determine wind orientation relative to beach angle:
    - Onshore: ±45° from directly onshore
    - Sideshore: 45°-135°
    - Offshore: >135°
    """
    relative_angle = (wind_dir - beach_angle) % 360
    if relative_angle > 180:
        relative_angle = 360 - relative_angle

    if relative_angle <= 45:
        return "onshore"
    elif relative_angle <= 135:
        return "sideshore"
    else:
        return "offshore"


def directional_shadowing_multiplier(direction, jetty_obstructions):
    # Check if direction is within ±45° of obstruction_direction (handling circular wraparound)
    for obstruction_direction in jetty_obstructions:
        if (
            min(
                abs(direction - obstruction_direction),
                360 - abs(direction - obstruction_direction),
            )
            <= 90
        ):
            return 0.7  # reduce breaking height by 30%
    return 1.0  # no reduction otherwise


def solve_breaking_wave_heights_from_swell(
    buoydata: surfpy.BuoyData,
    location: surfpy.Location,
    jetty_obstructions: list[int] | None = None,
    wind=None,
):
    # Convert to metric units temporarily
    old_unit = buoydata.unit
    if buoydata.unit != surfpy.units.Units.metric:
        buoydata.change_units(surfpy.units.Units.metric)

    breaking_heights = []

    # Calculate wave heights for all swells before finding total surf energy
    for swell in cast(list[surfpy.Swell], buoydata.swell_components):
        height = swell.wave_height
        period = swell.period
        direction = swell.direction

        # Calculate incident angle for this swell
        incident_angle = abs(direction - location.angle) % 360
        if incident_angle > 180:
            incident_angle = 360 - incident_angle

        # Ignore swells coming from behind the beach
        if incident_angle > 90:
            logging.debug(
                "90 degree Incident Angle indicates swell is coming from behind the beach and should be ignored at %s",
                location.name,
            )
            breaking_heights.append("Invalid incident angle")
            continue

        # Calculate breaking wave height for this swell
        wave_breaking_height, _ = surfpy.tools.breaking_characteristics(
            period,
            incident_angle,
            height,
            location.slope,
            location.depth,
        )

        # Apply 0.8 breaking coefficient
        adjusted_height = 0.8 * wave_breaking_height
        breaking_heights.append(adjusted_height)

    # Combine using quadrature sum: total surf energy from all swells
    if any(isinstance(h, (int, float)) for h in breaking_heights):
        combined_breaking_height = math.sqrt(
            sum(h**2 for h in breaking_heights if isinstance(h, (int, float)))
        )
        min_height = combined_breaking_height / 1.4
    else:
        buoydata.maximum_breaking_height = 0
        buoydata.minimum_breaking_height = 0
        return

    # Apply wind adjustment if provided
    if isinstance(combined_breaking_height, (int, float)) and buoydata:
        wind_speed = getattr(wind, "speed", 0)
        wind_direction = getattr(wind, "direction", 0)

        wind_type = classify_wind_relative_to_beach(wind_direction, location.angle)

        if wind_speed >= 13:
            if wind_type == "onshore":
                wind_penalty = -0.4  # range: -0.25 to -0.5 ft
            elif wind_type == "sideshore":
                wind_penalty = -0.15  # range: -0.1 to -0.2 ft
            else:  # offshore
                wind_penalty = 0.1
        else:
            if wind_type == "offshore":
                wind_penalty = 0.2
            else:
                wind_penalty = 0.0

        combined_breaking_height += wind_penalty
        min_height = combined_breaking_height / 1.4

    # Store results in buoydata
    if jetty_obstructions and len(jetty_obstructions) > 0:
        factor = directional_shadowing_multiplier(direction, jetty_obstructions)
        buoydata.maximum_breaking_height = combined_breaking_height * factor
        buoydata.minimum_breaking_height = min_height * factor
    else:
        buoydata.maximum_breaking_height = combined_breaking_height
        buoydata.minimum_breaking_height = min_height

    # Restore original units
    if old_unit != buoydata.unit:
        buoydata.change_units(old_unit)
