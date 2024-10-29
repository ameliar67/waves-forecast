import matplotlib.pyplot as plt
import surfpy
import matplotlib.dates as mdates
from cache import Cache
from new_data import retrieve_new_data
import pickle
import datetime


def get_wave_forecast(
    wave_location: surfpy.Location,
    wind_location: surfpy.Location,
    wave_model: surfpy.WaveModel,
    cache: Cache,
    hours_to_forecast=24,
) -> list[surfpy.buoydata.BuoyData] | None:
    key = f"{wave_location.name}"
    cache_item = cache.get_item(key)
    print("key", key)

    if cache_item is not None:
        result = pickle.loads(cache_item)
        return result

    result = retrieve_new_data(wave_model, hours_to_forecast, wave_location, wind_location)
    expires_at = datetime.datetime.now().day + 1
    result_cache_value = pickle.dumps(result)
    cache.set_item(key, result_cache_value, expires_at)

    return result


def get_chart(
    forecast: list[surfpy.buoydata.BuoyData], units: str = surfpy.units.Units.metric
):
    for d in forecast:
        d.change_units(units)

    maxs = [x.maximum_breaking_height for x in forecast]
    mins = [x.minimum_breaking_height for x in forecast]
    summary = [x.wave_summary.wave_height for x in forecast]
    times = [x.date for x in forecast]

    fig = plt.figure(figsize=(25, 10))
    ax = fig.subplots()
    ax.plot(times, maxs, c="green")
    ax.plot(times, mins, c="blue")
    ax.plot(times, summary, c="red")
    date_format = mdates.DateFormatter("%A %d %B\n%Y\n%H:%M")
    ax.xaxis.set_major_formatter(date_format)
    ax.set_xlabel("Date and Time")
    ax.set_ylabel(f"Breaking Wave Height ({forecast[0].unit})")
    ax.grid(True)

    return fig
