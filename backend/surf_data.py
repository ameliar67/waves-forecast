import datetime
import surfpy
from cache import Cache
from data_retrieval import retrieve_new_data
import json
import base64
from io import BytesIO
from typing import TypedDict


class WaveForecastData(TypedDict):
    chart: str
    average_wave_height: float
    weather_alerts: str | None


def get_wave_forecast(
    wave_model: str,
    cache: Cache,
    location_id: str,
    selected_location: str,
    lat=str,
    lon=str,
    hours_to_forecast=24,
) -> WaveForecastData:
    cache_encoding = "utf-8"
    key = f"ttl-short/forecast/v1/{location_id}"
    cache_item = cache.get_item(key, max_age=datetime.timedelta(days=1))
    if cache_item is not None:
        return json.loads(cache_item.decode(cache_encoding))

    # call retrieve_new_data for new forecast
    location = surfpy.Location(lat, lon, altitude=0, name=selected_location)
    location.depth = 10.0
    location.angle = 200.0
    location.slope = 0.28

    forecast_data = retrieve_new_data(wave_model, hours_to_forecast, location)

    img = BytesIO()
    forecast_data["chart"].savefig(img, format="png")
    plot_base64_image = base64.b64encode(img.getvalue()).decode("utf8")

    wave_height = forecast_data["average_wave_height"]
    data = {
        "chart": plot_base64_image,
        "average_wave_height": wave_height,
        "weather_alerts": forecast_data["weather_alerts"],
        "air_temperature": forecast_data["air_temperature"],
        "short_forecast": forecast_data["short_forecast"],
        "wind_speed": forecast_data["wind_speed"],
        "wind_direction": forecast_data["wind_direction"],
    }

    # set_item in cache
    cache.set_item(key, json.dumps(data).encode(cache_encoding))
    return data
