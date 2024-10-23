import matplotlib.pyplot as plt
import surfpy
import matplotlib.dates as mdates

def get_wave_forecast(
    wave_location: surfpy.Location,
    wind_location: surfpy.Location,
    wave_model: surfpy.WaveModel,
    hours_to_forecast=24,
) -> list[surfpy.buoydata.BuoyData] | None:
    wave_grib_data = wave_model.fetch_grib_datas(0, hours_to_forecast)
    raw_wave_data = wave_model.parse_grib_datas(wave_location, wave_grib_data)

    if not raw_wave_data:
        return None

    buoy_data = wave_model.to_buoy_data(raw_wave_data)
    weather_data = surfpy.WeatherApi.fetch_hourly_forecast(wind_location)
    wave_data = surfpy.merge_wave_weather_data(buoy_data, weather_data)

    for d in wave_data:
        d.solve_breaking_wave_heights(wave_location)
 
    return wave_data

def get_chart(forecast: list[surfpy.buoydata.BuoyData],
              units: str = surfpy.units.Units.metric):
    for d in forecast:
        d.change_units(units)

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
