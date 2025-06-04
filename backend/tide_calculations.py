def calculate_tide_intervals(tide_events, hour_interval_hours):
    """
    Interpolates tide levels between known tide events at a specified interval (in hours),
    and normalizes the water level between 0 and 1.
    """
    from datetime import timedelta

    # Step 1: Get min and max from original tide events
    levels = [event.water_level for event in tide_events]
    min_level = min(levels)
    max_level = max(levels)

    tide_data = []

    for i in range(len(tide_events) - 1):
        start = tide_events[i]
        end = tide_events[i + 1]

        time_diff_hours = (end.date - start.date).total_seconds() / 3600
        num_steps = int(time_diff_hours // hour_interval_hours)

        level_step = (end.water_level - start.water_level) / num_steps

        for step in range(num_steps + 1):
            interpolated_time = start.date + timedelta(hours=hour_interval_hours * step)
            interpolated_level = start.water_level + level_step * step
            normalized_level = normalize(interpolated_level, min_level, max_level)

            tide_phase = "Incoming Tide" if end.tidal_event == 'H' else "Ebb Tide"
            tide_label = start.tidal_event if step == 0 else (end.tidal_event if step == num_steps else tide_phase)

            tide_data.append({
                'timestamp': interpolated_time,
                'water_level': interpolated_level,
                'normalized_level': normalized_level,
                'tidal_event': tide_label
            })

    return tide_data

def normalize(value, min_level, max_level):
    return (value - min_level) / (max_level - min_level) if max_level > min_level else 0.0
