from surfpy import units, tools
import math


def solve_breaking_wave_heights_from_swell(buoydata, location):
    # Convert to metric units temporarily
    old_unit = buoydata.unit
    if buoydata.unit != units.Units.metric:
        buoydata.change_units(units.Units.metric)

    breaking_heights = []

    # Calculate wave heights for all swells before finding total surf energy
    for swell in buoydata.swell_components:
        height = swell.wave_height
        period = swell.period
        direction = swell.direction

        # Calculate incident angle for this swell
        incident_angle = abs(direction - location.angle) % 360
        if incident_angle > 180:
            incident_angle = 360 - incident_angle

        # > 90 degree Incident Angle indicates swell is coming from behind the beach and should be ignored
        if incident_angle > 90:
            continue

        # Calculate breaking wave height for this swell
        wave_breaking_height, _ = tools.breaking_characteristics(
            period, incident_angle, height, location.slope, location.depth
        )

        # Apply 0.8 breaking coefficient
        adjusted_height = 0.8 * wave_breaking_height

        breaking_heights.append(adjusted_height)

    # Combine using quadrature sum: total surf energy from all swells
    if breaking_heights:
        combined_breaking_height = math.sqrt(sum(h**2 for h in breaking_heights))
        min_height = combined_breaking_height / 1.4
    else:
        combined_breaking_height = 0
        min_height = 0

    # Store results in buoydata
    buoydata.maximum_breaking_height = combined_breaking_height
    buoydata.minimum_breaking_height = min_height

    # Restore original units
    if old_unit != buoydata.unit:
        buoydata.change_units(old_unit)
