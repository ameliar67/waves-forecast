import base64
import surf_data
import surfpy
import xml.etree.ElementTree as ET
import sys
import sqlite3

sys.path.insert(0, "..")

from flask import Flask, render_template, request
from io import BytesIO

app = Flask(__name__)

locations_dict = {}

tree = ET.parse("../libs/surfpy/surfpy/tests/data/activestations.xml")
root = tree.getroot()
for child in root:
    locations_dict[child.attrib["name"]] = {
        "id": child.attrib["id"],
        "longitude": float(child.attrib["lon"]),
        "latitude": float(child.attrib["lat"]),
    }

def get_db_connection():
    conn = sqlite3.connect("database.db", detect_types=sqlite3.PARSE_COLNAMES)
    return conn

connection = get_db_connection()
with open("schema.sql") as f:
    connection.executescript(f.read())

def generateWaveForecast(selectedLocation):
    lat = locations_dict[selectedLocation]["latitude"]
    lon = locations_dict[selectedLocation]["longitude"]
    location = surfpy.Location(lat, lon, altitude=0, name=selectedLocation)
    location.depth = 10.0
    location.angle = 200.0
    location.slope = 0.28

    wave_forecast = surf_data.get_wave_forecast(
        wave_location=location,
        wind_location=location,
        wave_model=surfpy.wavemodel.us_west_coast_gfs_wave_model(),
    )

    if not wave_forecast:
        raise ValueError("Failed to get forecast from NOAA")

    return wave_forecast


def generateImage(dataforImage):
    img = BytesIO()
    fig = surf_data.get_chart(dataforImage, surfpy.units.Units.english)
    fig.savefig(img, format="png")
    plot_base64_image = base64.b64encode(img.getvalue()).decode("utf8")

    return plot_base64_image


@app.route("/", methods=["GET", "POST"])
def location_selection():
    return render_template("index.html", locations=locations_dict.keys())


@app.route("/forecast.html", methods=["GET", "POST"])
def wave_forecast():
    selectedLocation = request.form.get("location")
    waves = generateWaveForecast(selectedLocation)
    image = generateImage(waves)

    summary = [x.wave_summary.wave_height for x in waves]

    return render_template(
        "forecast.html",
        info=summary,
        location=selectedLocation,
        plot_url=image,
        current_wave_height=round(summary[0]),
        locations=locations_dict.keys(),
        selectedLocation=selectedLocation,
    )


if __name__ == "__main__":
    app.run(debug=True)
