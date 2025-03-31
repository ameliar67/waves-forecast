import logging
from typing import TypedDict
import surfpy
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


async def get_response(session: aiohttp.ClientSession, url: str) -> bytes:
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.read()
    except aiohttp.ClientError as e:
        logging.error(f"Failed to fetch data from {url}: {e}")
        return b""


async def fetch_multiple_urls(urls: list[str]) -> list[bytes]:
    async with aiohttp.ClientSession() as session:
        tasks = [get_response(session, url) for url in urls]
        return await asyncio.gather(*tasks)


async def fetch_active_weather_alerts(location: Location) -> dict:
    url = f"https://api.weather.gov/alerts/active?point={location.latitude},{location.longitude}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                resp.raise_for_status()
                resp_json = await resp.json()
                return resp_json
    except aiohttp.ClientError as e:
        logging.error(f"Failed to fetch weather alerts for {location}: {e}")
        return {}


async def retrieve_new_data(
    wave_model, hours_to_forecast, location, conversion_rate
) -> WaveForecastData | None:

    wave_data = {}

    # Generate URLs for fetching grib data
    urls = wave_model.create_grib_urls(0, hours_to_forecast)

    # Fetch GRIB data in parallel
    grib_datas = await fetch_multiple_urls(urls)

    for grib_data in grib_datas:
        wave_model.parse_grib_data(location, grib_data, wave_data)

    if not wave_data:
        return None

    # Turn NOAA model data into buoy data
    buoy_data = wave_model.to_buoy_data(wave_data)

    # Fetch weather data
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

    alerts = await fetch_active_weather_alerts(location)

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
