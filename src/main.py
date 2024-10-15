import base64
import surf_data
import surfpy
import sys

from flask import Flask, render_template
from io import BytesIO

app = Flask(__name__)

location = surfpy.Location(46.89, -124.10, altitude=0.0, name="Westport, WA")
location.depth = 10.0
location.angle = 200.0
location.slope = 0.28

wave_forecast = surf_data.get_wave_forecast(
    wave_location=location,
    wind_location=location,
    wave_model=surfpy.wavemodel.us_west_coast_gfs_wave_model(),
)
if not wave_forecast:
    print("Failed to get forecast from NOAA")
    sys.exit(1)

summary = [x.wave_summary.wave_height for x in wave_forecast]

img = BytesIO()
fig = surf_data.get_chart(wave_forecast, surfpy.units.Units.english)
fig.savefig(img, format="png")
img.seek(0)
plot_base64_image = base64.b64encode(img.getvalue()).decode("utf8")


@app.route("/")
def wave_forecast():
    return render_template(
        "index.html",
        info=summary,
        location=location.name,
        plot_url=plot_base64_image,
        current_wave_height=round(summary[0]),
    )


if __name__ == "__main__":
    app.run(debug=True)
