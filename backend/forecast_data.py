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
    wave_model: surfpy.WaveModel,
    cache: Cache,
    location_id: str,
    selected_location: str,
    lat=str,
    lon=str,
    hours_to_forecast=24,
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

    forecast_data = retrieve_new_data(
        wave_model, hours_to_forecast, location, conversion_rate
    )

    # Generate graph
    img = BytesIO()
    forecast_data["chart"].savefig(img, format="png")
    plot_base64_image = base64.b64encode(img.getvalue()).decode("utf8")

    # Prepare the forecast data to return
    wave_height = forecast_data["average_wave_height"]
    data = {
        "chart": plot_base64_image,
        "average_wave_height": wave_height,
        "weather_alerts": forecast_data["weather_alerts"],
        "air_temperature": forecast_data["air_temperature"],
        "short_forecast": forecast_data["short_forecast"],
        "wind_speed": forecast_data["wind_speed"],
        "wind_direction": forecast_data["wind_direction"],
        "hourly_forecast": forecast_data["hourly_forecast"],
        "forecast_hours": forecast_data["forecast_hours"],
        "forecast_dates": forecast_data["forecast_dates"],
    }

    # Cache the newly fetched data
    cache.set_item(key, json.dumps(data).encode(cache_encoding))
    return data
