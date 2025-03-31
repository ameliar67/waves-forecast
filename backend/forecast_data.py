import datetime
import json

import surfpy
from cache import Cache
from data_retrieval import WaveForecastData, retrieve_new_data


async def get_wave_forecast(
    wave_model: surfpy.WaveModel,
    cache: Cache,
    location_id: str,
    selected_location: str,
    lat=str,
    lon=str,
    hours_to_forecast=384,
) -> WaveForecastData:
    cache_encoding = "utf-8"
    key = f"ttl-short/forecast/v1/{location_id}"

    # Cache check: return if found
    if (
        cache_item := cache.get_item(key, max_age=datetime.timedelta(days=1))
    ) is not None:
        return json.loads(cache_item.decode(cache_encoding))

    # Cache miss: Retrieve new data

    # Conversion rate for metric to imperial (multiply result by 3.281)
    # Currently surfpy module returns metric data
    conversion_rate = 3.281
    location = surfpy.Location(lat, lon, altitude=0, name=selected_location)
    location.depth, location.angle, location.slope = 10.0, 200.0, 0.28

    data = await retrieve_new_data(
        wave_model, hours_to_forecast, location, conversion_rate
    )

    # Cache the newly fetched data
    cache.set_item(key, json.dumps(data).encode(cache_encoding))
    return data
