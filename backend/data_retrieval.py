from math import isnan

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import surfpy
from config import app_session
from surfpy import units
from surfpy.location import Location


def change_units(content, new_units, old_unit):

    for d in content:

        if d.wave_summary is not None:
            d.wave_summary.change_units(new_units)
        for swell in d.swell_components:
            swell.change_units(new_units)

        d.minimum_breaking_height = units.convert(
            d.minimum_breaking_height, units.Measurement.length, old_unit, d.unit
        )
        d.maximum_breaking_height = units.convert(
            d.maximum_breaking_height, units.Measurement.length, old_unit, d.unit
        )
        d.wind_speed = units.convert(
            d.wind_speed, units.Measurement.speed, old_unit, d.unit
        )
        d.air_temperature = units.convert(
            d.air_temperature, units.Measurement.temperature, old_unit, d.unit
        )
        d.pressure = units.convert(
            d.pressure, units.Measurement.pressure, old_unit, d.unit
        )

    return content


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


def get_chart(forecast, conversion_rate):

    maxs = [x.maximum_breaking_height * conversion_rate for x in forecast]
    mins = [x.minimum_breaking_height * conversion_rate for x in forecast]
    summary = [x.wave_summary.wave_height * conversion_rate for x in forecast]
    times = [x.date for x in forecast]

    fig = plt.figure(figsize=(25, 10))
    ax = fig.subplots()
    ax.plot(times, maxs, c="green", label="max")
    ax.plot(times, mins, c="blue", label="min")
    ax.plot(times, summary, c="red", label="average")
    date_format = mdates.DateFormatter("%A %d %B\n%Y\n%H:%M")
    ax.xaxis.set_major_formatter(date_format)
    ax.set_xlabel("Date and Time")
    ax.set_ylabel(f"Breaking Wave Height ({forecast[0].unit})")
    ax.legend(loc="upper left")
    ax.grid(True)

    return fig


def fetch_active_weather_alerts(location: Location, api_root_url: str) -> dict:
    # https://api.weather.gov/alerts/active?point=46.221924,-123.816882

    url = f"{api_root_url}alerts/active?point={location.latitude},{location.longitude}"
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
) -> plt.Figure:

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

    air_temperature = getattr(
        weather_data[0], "air_temperature", "No temperature forecast available"
    )
    short_forecast = getattr(weather_data[0], "short_forecast", "No forecast available")
    wind_speed = getattr(weather_data[0], "wind_speed", "No wind speed available")
    wind_direction = getattr(
        weather_data[0], "wind_compass_direction", "No wind direction available"
    )

    alerts = fetch_active_weather_alerts(location, "https://api.weather.gov/")
    wave_data = merge_wave_weather_data(buoy_data, weather_data)

    for d in wave_data:
        d.solve_breaking_wave_heights(location)

    current_wave_height = round(wave_data[0].wave_summary.wave_height * conversion_rate)

    chart = get_chart(wave_data, conversion_rate)
    hourly_forecast, forecast_hours, forecast_dates = [], [], []

    for x in wave_data:
        hourly_forecast.append(x.wave_summary.wave_height * conversion_rate)

        # Get the hour from the date
        hour = x.date.hour  # Extracts the hour from the datetime object

        # Check if the hour is later than 21:00 (9 PM) or earlier than 6:00 AM
        if hour > 21 or hour < 6:
            continue

        # Append forecast hours and dates
        forecast_hours.append(x.date.strftime("%H:%M"))
        forecast_dates.append(x.date.strftime("%m-%d-%Y"))

    alerts_list = alerts.get("features", [])
    headline = (
        alerts_list[0].get("properties", {}).get("headline", None)
        if alerts_list
        else None
    )

    forecast_data = {
        "chart": chart,
        "average_wave_height": current_wave_height,
        "weather_alerts": headline or "None",
        "air_temperature": air_temperature,
        "short_forecast": short_forecast,
        "wind_speed": wind_speed,
        "wind_direction": wind_direction,
        "hourly_forecast": hourly_forecast,
        "forecast_hours": forecast_hours,
        "forecast_dates": forecast_dates,
    }

    return forecast_data
