import asyncio
from collections import defaultdict
import datetime
import logging
import math
from typing import TypedDict, cast

import aiohttp
import surfpy

from context import ForecastContext
from grib_parser import GribTimeWindow, parse_grib_data
from swell_calculations import solve_breaking_wave_heights_from_swell
from tide_calculations import calculate_tide_intervals
from wave_rating import surf_quality_rating


class HourlyForecastSummary(TypedDict):
    date: str
    max_breaking_height: float
    min_breaking_height: float
    wave_height: float
    surf_ratng: str
    swell_period: float


class WaveForecastData(TypedDict):
    generated_at: str
    weather_alerts: str | None
    hourly_forecast: list[HourlyForecastSummary]
    tide_forecast: list
    selected_location: str


EMPTY_FORECAST_DATA = {
    "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "weather_alerts": [],
    "hourly_forecast": [
        {
            "chart": None,
            "current_wave_height": 0,
            "alerts": "No forecast available",
            "air_temperature": "No forecast available",
            "wind_speed": "No forecast available",
            "wind_direction": "No forecast available",
            "short_forecast": "No forecast available",
        }
    ],
    "tide_forecast": [],
    "selected_location": "",
}


async def get_response(context: ForecastContext, url: str) -> bytes:
    try:
        async with context.http_session.get(url) as response:
            response.raise_for_status()
            return await response.read()
    except aiohttp.ClientError:
        logging.exception("Failed to fetch data from %s", url)
        return b""


async def fetch_active_weather_alerts(
    context: ForecastContext, location: surfpy.Location
) -> dict:
    url = f"https://api.weather.gov/alerts/active?point={location.latitude},{location.longitude}"
    try:
        logging.info("Fetching weather alerts from url %s", url)
        async with context.http_session.get(url) as resp:
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


async def get_wave_model_grib(
    context: ForecastContext, url: str
) -> GribTimeWindow | None:
    try:
        response = await get_response(context, url)
        return parse_grib_data(response) if len(response) else None
    except:
        logging.exception("Failed to get GRIB data from %s", url)
        return None


async def get_wave_forecast_models(
    context: ForecastContext, wave_model: surfpy.WaveModel, hours: int
) -> list[GribTimeWindow]:
    futures = [
        context.get_cached_or_compute(u, get_wave_model_grib)
        for u in wave_model.create_grib_urls(0, hours)
    ]
    grib_datas = await asyncio.gather(*futures)
    return [g for g in grib_datas if g is not None]


def is_data_all_zeros(data, keys):
    return all(
        key in data
        and isinstance(data[key], list)
        and all(value == 0.0 for value in data[key])
        for key in keys
    )


def combined_swell_period(swell_components):
    """
    Calculate the energy-weighted average swell period from a list of swell components.

    Args:
        swell_components (list of dict or objects): Each with 'period' and 'height' properties.

    Returns:
        float: Combined swell period in seconds.
    """
    if not swell_components:
        return 0

    weighted_sum = 0
    energy_sum = 0

    for swell in swell_components:
        period = swell.period
        height = swell.wave_height

        if period is None or height is None:
            continue  # skip incomplete data

        energy = height**2
        weighted_sum += period * energy
        energy_sum += energy

    return weighted_sum / energy_sum if energy_sum > 0 else 0


async def retrieve_new_data(
    context: ForecastContext,
    wave_model: surfpy.WaveModel,
    hours_to_forecast: int,
    location: surfpy.Location,
    tide_stations: list[str] | None,
    jetty_obstructions: list[int],
) -> WaveForecastData:
    location_resolution = 0.167
    wave_data = defaultdict(list)

    # Retrieve grib data from NOAA for given location
    forecast_models = await get_wave_forecast_models(
        context, wave_model, hours_to_forecast
    )
    for m in forecast_models:
        wave_data["time"].append(m.time)
        for key, func in m.data_funcs.items():
            func_val = func(location, location_resolution)
            wave_data[key].append(func_val)

    # If grib data is empty return early
    if not wave_data:
        logging.warning(
            "No wave data available after parsing GRIB data for %f,%f",
            location.latitude,
            location.longitude,
        )
        return cast(WaveForecastData, {**EMPTY_FORECAST_DATA.copy()})

    # Turn NOAA model grib data into buoy data
    buoy_data: list[surfpy.BuoyData] = wave_model.to_buoy_data(wave_data)

    # Return empty data if shww (significant wave height), wvdir (wave direction) and shts(significant height of total swell) are all zeroes
    # If all of these fields are arrays of zeroes there is a problem with the data rather than a forecast for flat waves
    # which would result in an inaccurate forecast
    if len(buoy_data) == 0 or is_data_all_zeros(wave_data, ["shww", "wvdir", "shts"]):
        logging.warning(
            "No buoy data available for location %f,%f",
            location.latitude,
            location.longitude,
        )
        return cast(WaveForecastData, {**EMPTY_FORECAST_DATA.copy()})

    # Fetch weather data
    weather_data, alerts = await asyncio.gather(
        fetch_hourly_forecast_async(location),
        fetch_active_weather_alerts(context, location),
    )

    alerts_list = alerts.get("features", [])
    headline = (
        alerts_list[0].get("properties", {}).get("headline", None)
        if alerts_list
        else None
    )

    start_date = datetime.datetime.today()
    end_date = start_date + datetime.timedelta(days=16)

    # use two tide stations - one as a backup in case the first has no data
    station_objects: list[surfpy.TideStation | None] = [None] * 2

    for station in context.tide_stations.stations:
        if tide_stations and station.station_id == tide_stations[0]:
            station_objects[0] = station
        if tide_stations and station.station_id == tide_stations[1]:
            station_objects[1] = station

    for s in station_objects:
        if s:
            tide_data = s.fetch_tide_data(
                start_date,
                end_date,
                interval=surfpy.TideStation.DataInterval.high_low,
                unit=surfpy.units.Units.metric,
            )
            if tide_data and tide_data[0]:
                break

    weather_data_index = 0
    tide_data_iterator = 0
    tides_with_intervals = []
    if tide_data and tide_data[0]:
        tides_with_intervals = calculate_tide_intervals(tide_data[0], 3)

    hourly_forecast = []
    for x in buoy_data:
        solve_breaking_wave_heights_from_swell(x, location, jetty_obstructions)
        valid_index = 0 <= weather_data_index < len(weather_data)
        weather_entry = weather_data[weather_data_index] if valid_index else None

        if x.maximum_breaking_height == "Invalid Incident Angle":
            return cast(WaveForecastData, {**EMPTY_FORECAST_DATA.copy()})

        swell_period = combined_swell_period(x.swell_components)

        if (
            len(tides_with_intervals) > 0
            and weather_entry
            and weather_entry.wind_speed is not None
        ):
            surf_rating = surf_quality_rating(
                x.maximum_breaking_height,
                swell_period,
                weather_entry.wind_speed,
                tides_with_intervals[tide_data_iterator]["normalized_level"],
            )
        else:
            surf_rating = "No surf rating currently available"

        # keep tide intervals up to date
        if (
            tide_data_iterator < (len(tides_with_intervals) - 1)
            and x.date > tides_with_intervals[tide_data_iterator]["timestamp"]
        ):
            tide_data_iterator += 1

        hourly_forecast.append(
            {
                "date": x.date.isoformat() if x.date is not None else None,
                "max_breaking_height": (
                    x.maximum_breaking_height
                    if not math.isnan(x.maximum_breaking_height)
                    else None
                ),
                "min_breaking_height": (
                    x.minimum_breaking_height
                    if not math.isnan(x.minimum_breaking_height)
                    else None
                ),
                "air_temperature": (
                    weather_entry.air_temperature
                    if weather_entry
                    and weather_entry.air_temperature is not None
                    and not math.isnan(weather_entry.air_temperature)
                    else None
                ),
                "wind_direction": (
                    weather_entry.wind_direction
                    if weather_entry
                    and weather_entry.wind_direction is not None
                    and not math.isnan(weather_entry.wind_direction)
                    else None
                ),
                "wind_speed": (
                    weather_entry.wind_speed
                    if weather_entry
                    and weather_entry.wind_speed is not None
                    and not math.isnan(weather_entry.wind_speed)
                    else None
                ),
                "short_forecast": (
                    weather_entry.short_forecast
                    if weather_entry and weather_entry.short_forecast
                    else None
                ),
                "wave_height": (
                    x.wave_summary.wave_height if x.wave_summary is not None else None
                ),
                "surf_rating": surf_rating,
                "swell_period": round(swell_period),
            }
        )

    # if this is triggered still return existing wave data
    if len(weather_data) == 0:
        logging.warning(
            "No forecast available for location %f,%f",
            location.latitude,
            location.longitude,
        )
        return cast(
            WaveForecastData,
            {
                **EMPTY_FORECAST_DATA.copy(),
                "weather_alerts": headline or "None",
                "hourly_forecast": hourly_forecast,
            },
        )

    tide_forecast = []

    # could add forecast.water_level later on if it's relevant to forecast calculation
    if tide_data and tide_data[0]:
        for forecast in tide_data[0]:
            tide_forecast.append(
                {
                    "date": forecast.date.isoformat(),
                    "tidal_event": forecast.tidal_event,
                }
            )

    return {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "weather_alerts": headline or "None",
        "hourly_forecast": hourly_forecast,
        "tide_forecast": tide_forecast,
        "selected_location": location.name,
    }
