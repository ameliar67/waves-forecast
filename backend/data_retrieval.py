import asyncio
from collections import defaultdict
import datetime
import logging
import math
from typing import TypedDict

import aiohttp
import surfpy
from grib_parser import GribTimeWindow, parse_grib_data

http_session = aiohttp.ClientSession()
http_session.headers["User-Agent"] = "waves-forecast/1.0.0"


class HourlyForecastSummary(TypedDict):
    date: str
    max_breaking_height: float
    min_breaking_height: float
    wave_height: float


class WaveForecastData(TypedDict):
    selected_location: str
    generated_at: str
    average_wave_height: int
    weather_alerts: str | None
    air_temperature: int | str
    short_forecast: str
    wind_speed: int | str
    wind_direction: str
    hourly_forecast: list[HourlyForecastSummary]


# Setup logging to track the execution flow
logging.basicConfig(level=logging.INFO)  # Set to INFO level for less verbosity


async def get_response(session: aiohttp.ClientSession, url: str) -> bytes:
    try:
        logging.info("Fetching data from %s", url)
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.read()
    except aiohttp.ClientError:
        logging.exception("Failed to fetch data from %s", url)
        return b""


async def fetch_active_weather_alerts(location: surfpy.Location) -> dict:
    url = f"https://api.weather.gov/alerts/active?point={location.latitude},{location.longitude}"
    try:
        logging.info("Fetching weather alerts from url %s", url)
        async with http_session.get(url) as resp:
            resp.raise_for_status()
            resp_json = await resp.json()
            return resp_json
    except aiohttp.ClientError:
        logging.exception("Failed to fetch weather alerts from %s", url)
        return {}


async def fetch_hourly_forecast_async(
    location: surfpy.Location,
) -> list[surfpy.BuoyData]:
    try:
        logging.info(
            "Fetching hourly forecast for location %f,%f",
            location.latitude,
            location.longitude,
        )
        return await asyncio.to_thread(
            surfpy.WeatherApi.fetch_hourly_forecast, location
        )
    except:
        logging.exception(
            "Failure fetching hourly forecast for location %f,%f - returning empty result",
            location.latitude,
            location.longitude,
        )
        return []


async def get_wave_model_grib(url) -> GribTimeWindow | None:
    try:
        response = await get_response(http_session, url)
        return parse_grib_data(response) if len(response) else None
    except:
        logging.exception("Failed to get GRIB data from %s", url)
        return None


async def get_wave_forecast_models(
    wave_model: surfpy.WaveModel, hours: int
) -> list[GribTimeWindow]:
    futures = [get_wave_model_grib(u) for u in wave_model.create_grib_urls(0, hours)]
    grib_datas = await asyncio.gather(*futures)
    return [g for g in grib_datas if g is not None]


EMPTY_FORECAST_DATA = {
    "chart": None,
    "current_wave_height": 0,
    "alerts": "No forecast available",
    "air_temperature": "No forecast available",
    "wind_speed": "No forecast available",
    "wind_direction": "No forecast available",
    "short_forecast": "No forecast available",
}


async def retrieve_new_data(
    wave_model: surfpy.WaveModel,
    hours_to_forecast: int,
    location: surfpy.Location,
) -> WaveForecastData | None:
    location_resolution = 0.167
    wave_data = defaultdict(list)

    forecast_models = await get_wave_forecast_models(wave_model, hours_to_forecast)
    for m in forecast_models:
        wave_data["time"].append(m.time)
        for key, func in m.data_funcs.items():
            func_val = func(location, location_resolution)
            wave_data[key].append(func_val)

    if not wave_data:
        logging.warning(
            "No wave data available after parsing GRIB data for %f,%f",
            location.latitude,
            location.longitude,
            wave_model.description,
        )
        return None

    # Turn NOAA model data into buoy data
    buoy_data: list[surfpy.BuoyData] = wave_model.to_buoy_data(wave_data)

    if len(buoy_data) == 0:
        logging.warning(
            "No buoy data available for location %f,%f",
            location.latitude,
            location.longitude,
        )
        return {**EMPTY_FORECAST_DATA.copy(), "wave_model": wave_model.description}

    # Fetch weather data
    weather_data, alerts = await asyncio.gather(
        fetch_hourly_forecast_async(location), fetch_active_weather_alerts(location)
    )

    alerts_list = alerts.get("features", [])
    headline = (
        alerts_list[0].get("properties", {}).get("headline", None)
        if alerts_list
        else None
    )

    weather_data_index = 0

    hourly_forecast = []
    for x in buoy_data:
        x.solve_breaking_wave_heights(location)
        while weather_data_index < (len(weather_data) - 1) and weather_data[weather_data_index].date < x.date:
            weather_data_index += 1

        hourly_forecast.append(
            {
                "date": x.date.isoformat(),
                "max_breaking_height": (
                    x.maximum_breaking_height
                    if not math.isnan(x.maximum_breaking_height)
                    else None
                ),
                "min_breaking_height": (
                    x.maximum_breaking_height
                    if not math.isnan(x.maximum_breaking_height)
                    else None
                ),
                "air_temperature": (
                    weather_data[weather_data_index].air_temperature
                    if not math.isnan(weather_data[weather_data_index].air_temperature)
                    else None
                ),
                "wind_direction": (
                    weather_data[weather_data_index].wind_direction
                    if not math.isnan(weather_data[weather_data_index].wind_direction)
                    else None
                ),
                "wind_speed": (
                    weather_data[weather_data_index].wind_speed
                    if not math.isnan(weather_data[weather_data_index].wind_speed)
                    else None
                ),
                "short_forecast": (
                    weather_data[weather_data_index].short_forecast
                    if weather_data[weather_data_index].short_forecast
                    else None
                ),
                "wave_height": x.wave_summary.wave_height,
            }
        )

    # if this is triggered still return existing wave data
    if len(weather_data) == 0:
        logging.warning(
            "No forecast available for location %f,%f",
            location.latitude,
            location.longitude,
        )
        return {
            **EMPTY_FORECAST_DATA.copy(),
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "weather_alerts": headline or "None",
            "hourly_forecast": hourly_forecast,
        }

    return {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "weather_alerts": headline or "None",
        "hourly_forecast": hourly_forecast,
    }
