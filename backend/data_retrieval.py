import logging
from math import isnan
from typing import TypedDict

import surfpy
from config import app_session
from surfpy.location import Location

class HourlyForecastSummary(TypedDict):
    date: str
    max_breaking_height: float
    min_breaking_height: float
    wave_height: float


class WaveForecastData(TypedDict):
    selected_location: str
    average_wave_height: int
    weather_alerts: str | None
    air_temperature: int | str
    short_forecast: str
    wind_speed: int | str
    wind_direction: str
    hourly_forecast: list[HourlyForecastSummary]

def merge_wave_weather_data(wave_data, weather_data):
    last_weather_index = 0

    for wave in wave_data:
        if wave.date > weather_data[-1].date:
            return wave_data

        for i in range(last_weather_index, len(weather_data)):
            weather = weather_data[i]
            if weather.date != wave.date:
                continue

            if weather.air_temperature is not None and not isnan(
                weather.air_temperature
            ):
                wave.air_temperature = weather.air_temperature
            wave.short_forecast = weather.short_forecast
            if weather.wind_speed is not None and not isnan(weather.wind_speed):
                wave.wind_speed = weather.wind_speed
            if weather.wind_direction is not None and not isnan(weather.wind_direction):
                wave.wind_direction = weather.wind_direction
            if weather.wind_compass_direction is not None:
                wave.wind_compass_direction = weather.wind_compass_direction
            last_weather_index = i
            break

    return wave_data


def fetch_active_weather_alerts(location: Location) -> dict:
    # https://api.weather.gov/alerts/active?point=46.221924,-123.816882

    url = f"https://api.weather.gov/alerts/active?point={location.latitude},{location.longitude}"
    resp = app_session.get(url)
    if not resp.ok:
        logging.error(
            f"Failed to fetch weather alerts for {location}: {resp.status_code} {resp.text}"
        )
        return {}

    resp_json = resp.json()
    return resp_json


def retrieve_new_data(
    wave_model, hours_to_forecast, location, conversion_rate
) -> WaveForecastData | None:

    wave_grib_data = wave_model.fetch_grib_datas(0, hours_to_forecast)
    raw_wave_data = wave_model.parse_grib_datas(location, wave_grib_data)

    if not raw_wave_data:
        return None

    buoy_data = wave_model.to_buoy_data(raw_wave_data)
    weather_data = surfpy.WeatherApi.fetch_hourly_forecast(location)

    if len(weather_data) == 0:
        forecast_data = {
            "chart": None,
            "current_wave_height": 0,
            "alerts": "No forecast available",
            "air_temperature": "No forecast available",
        }
        return forecast_data

    # Use default values for missing data
    air_temperature = getattr(
        weather_data[0], "air_temperature", "No temperature forecast available"
    )
    short_forecast = getattr(weather_data[0], "short_forecast", "No forecast available")
    wind_speed = getattr(weather_data[0], "wind_speed", "No wind speed available")
    wind_direction = getattr(
        weather_data[0], "wind_compass_direction", "No wind direction available"
    )

    alerts = fetch_active_weather_alerts(location)
    wave_data = merge_wave_weather_data(buoy_data, weather_data)

    for d in wave_data:
        d.solve_breaking_wave_heights(location)

    current_wave_height = round(wave_data[0].wave_summary.wave_height * conversion_rate)

    hourly_forecast = []
    for x in wave_data:
        hourly_forecast.append(
            {
                "date": x.date.isoformat(),
                "max_breaking_height": x.maximum_breaking_height * conversion_rate,
                "min_breaking_height": x.minimum_breaking_height * conversion_rate,
                "wave_height": x.wave_summary.wave_height * conversion_rate,
            }
        )

    alerts_list = alerts.get("features", [])
    headline = (
        alerts_list[0].get("properties", {}).get("headline", None)
        if alerts_list
        else None
    )

    return {
        "average_wave_height": current_wave_height,
        "weather_alerts": headline or "None",
        "air_temperature": air_temperature,
        "short_forecast": short_forecast,
        "wind_speed": wind_speed,
        "wind_direction": wind_direction,
        "hourly_forecast": hourly_forecast,
    }
