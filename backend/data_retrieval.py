import logging
from typing import TypedDict
import surfpy
from config import app_session
from surfpy.location import Location
import asyncio
import aiohttp


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


async def get_response(session: aiohttp.ClientSession, url: str):
    async with session.get(url) as response:
        return await response.read()


async def make_requests(urls):
    responses = []

    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            task = get_response(session, url)
            tasks.append(task)

        responses = await asyncio.gather(*tasks)

    return responses


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

    wave_data = {}

    # Generate URLs for fetching grib data
    urls = wave_model.create_grib_urls(0, hours_to_forecast)

    grib_datas = asyncio.run(make_requests(urls))

    for grib_data in grib_datas:
        wave_model.parse_grib_data(location, grib_data, wave_data)

    if not wave_data:
        return None

    # Turn NOAA model data into buoy data
    buoy_data = wave_model.to_buoy_data(wave_data)

    weather_data = surfpy.WeatherApi.fetch_hourly_forecast(location)

    if len(weather_data) == 0 or len(buoy_data) == 0:
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

    hourly_forecast = []
    for x in buoy_data:
        x.solve_breaking_wave_heights(location)
        hourly_forecast.append(
            {
                "date": x.date.isoformat(),
                "max_breaking_height": x.maximum_breaking_height * conversion_rate,
                "min_breaking_height": x.minimum_breaking_height * conversion_rate,
                "wave_height": x.wave_summary.wave_height * conversion_rate,
            }
        )

    current_wave_height = round(buoy_data[0].wave_summary.wave_height * conversion_rate)

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
