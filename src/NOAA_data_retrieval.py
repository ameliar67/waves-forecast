import surfpy
from math import isnan
from math import isnan
from surfpy import units
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

def change_units(content, new_units, old_unit):

    for d in content:

        if d.wave_summary is not None:
            d.wave_summary.change_units(new_units)
        for swell in d.swell_components:
            swell.change_units(new_units)

        d.minimum_breaking_height = units.convert(d.minimum_breaking_height, units.Measurement.length, old_unit, d.unit)
        d.maximum_breaking_height = units.convert(d.maximum_breaking_height, units.Measurement.length, old_unit, d.unit)
        d.wind_speed = units.convert(d.wind_speed, units.Measurement.speed, old_unit, d.unit)
        d.air_temperature = units.convert(d.air_temperature, units.Measurement.temperature, old_unit, d.unit)
        d.pressure = units.convert(d.pressure, units.Measurement.pressure, old_unit, d.unit)

    return content

def merge_wave_weather_data(wave_data, weather_data, units):
    last_weather_index = 0
    
    for wave in wave_data:
        wave.change_units(units.Units.metric)
        if wave.date > weather_data[-1].date:
            return wave_data

        for i in range(last_weather_index, len(weather_data)):
            weather = weather_data[i]
            if weather.date != wave.date:
                continue

            weather.change_units(units.Units.metric)
            if weather.air_temperature is not None and not isnan(weather.air_temperature):
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



def get_chart(
    forecast, units: str = surfpy.units.Units.metric
):

    forecast = change_units(forecast, units, units)

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


def retrieve_new_data(wave_model, hours_to_forecast, location):

    wave_grib_data = wave_model.fetch_grib_datas(0, hours_to_forecast)
    raw_wave_data = wave_model.parse_grib_datas(location, wave_grib_data)

    if not raw_wave_data:
        return None

    buoy_data = wave_model.to_buoy_data(raw_wave_data)
    weather_data = surfpy.WeatherApi.fetch_hourly_forecast(location)
    wave_data = merge_wave_weather_data(buoy_data, weather_data, units)

    for d in wave_data:
        d.solve_breaking_wave_heights(location)
    print(d.summary, "d.summary")

    res = change_units(wave_data, surfpy.units.Units.metric, surfpy.units.Units.metric)

    chart = get_chart(res)

    return chart
