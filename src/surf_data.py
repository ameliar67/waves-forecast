import matplotlib.pyplot as plt
import surfpy
import matplotlib.dates as mdates
import datetime
import sqlite3
import pickle
from new_data import retrieveNewData


def get_db_connection():
    conn = sqlite3.connect("database.db", detect_types=sqlite3.PARSE_COLNAMES)
    return conn


def get_wave_forecast(
    wave_location: surfpy.Location,
    wind_location: surfpy.Location,
    wave_model: surfpy.WaveModel,
    hours_to_forecast=24,
) -> list[surfpy.buoydata.BuoyData] | None:
    conn = get_db_connection()
    database_data = conn.execute("SELECT * FROM waveData").fetchall()

    for line in database_data:
        time = line[1]
        content = line[3]
        location = line[4]
        datetime_object = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S")

        if (
            datetime_object.day == datetime.datetime.now().day
            and location == wave_location.name
        ):
            wave_data = pickle.loads(content)
            conn.close()
            return wave_data

    conn.close()
    return retrieveNewData(wave_model, hours_to_forecast, wave_location, wind_location)


def get_chart(
    forecast: list[surfpy.buoydata.BuoyData], units: str = surfpy.units.Units.metric
):
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
