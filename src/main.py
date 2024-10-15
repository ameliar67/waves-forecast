import surfpy
import sys
import matplotlib.pyplot as plt
import base64
from io import BytesIO

from flask import Flask, render_template

app = Flask(__name__)

ri_wave_location = surfpy.Location(41.35, -71.4, altitude=0.0, name="Westport")
ri_wave_location.depth = 10.0
ri_wave_location.angle = 200.0
ri_wave_location.slope = 0.28
atlantic_wave_model = surfpy.wavemodel.atlantic_gfs_wave_model()

print("Fetching GFS Wave Data")
num_hours_to_forecast = 24  # One day forecast. Change to 384 to get a 16 day forecast
wave_grib_data = atlantic_wave_model.fetch_grib_datas(0, num_hours_to_forecast)
raw_wave_data = atlantic_wave_model.parse_grib_datas(ri_wave_location, wave_grib_data)

if raw_wave_data:
    data = atlantic_wave_model.to_buoy_data(raw_wave_data)
else:
    print("Failed to fetch wave forecast data")
    sys.exit(1)

print("Fetching local weather data")
ri_wind_location = surfpy.Location(46.89, -124.10, altitude=0.0, name="Westport")
weather_data = surfpy.WeatherApi.fetch_hourly_forecast(ri_wind_location)
surfpy.merge_wave_weather_data(data, weather_data)

for dat in data:
    dat.solve_breaking_wave_heights(ri_wave_location)
    dat.change_units(surfpy.units.Units.english)
json_data = surfpy.serialize(data)
with open("forecast.json", "w") as outfile:
    outfile.write(json_data)

maxs = [x.maximum_breaking_height for x in data]
mins = [x.minimum_breaking_height for x in data]
summary = [x.wave_summary.wave_height for x in data]
times = [x.date for x in data]

fig = plt.figure(figsize=(10, 6))
ax = fig.subplots()
ax.plot(times, maxs, c="green")
ax.plot(times, mins, c="blue")
ax.plot(times, summary, c="red")
ax.set_xlabel("Date and Time")
ax.set_ylabel("Breaking Wave Height (ft)")
ax.grid(True)


img = BytesIO()
fig.savefig(img, format="png")
img.seek(0)

plot_url = base64.b64encode(img.getvalue()).decode("utf8")


@app.route("/")
def wave_data():
    return render_template(
        "index.html", info=summary, location=ri_wave_location.name, plot_url=plot_url, current_wave_height=round(summary[0])
    )


if __name__ == "__main__":
    app.run(debug=True)
