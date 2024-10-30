import surf_data
import surfpy
import xml.etree.ElementTree as ET
import sys
from cache import Cache

sys.path.insert(0, "..")

from flask import Flask, render_template, request

app = Flask(__name__)
cache = Cache("database.db")
cache.migrate()

locations_dict = {}

tree = ET.parse("../libs/surfpy/surfpy/tests/data/activestations.xml")
root = tree.getroot()
for child in root:
    locations_dict[child.attrib["name"]] = {
        "id": child.attrib["id"],
        "longitude": float(child.attrib["lon"]),
        "latitude": float(child.attrib["lat"]),
    }

def generate_wave_forecast(selectedLocation):

    wave_forecast = surf_data.get_wave_forecast(
        wave_model=surfpy.wavemodel.us_west_coast_gfs_wave_model(),
        cache=cache,
        selectedLocation=selectedLocation,
        lat=locations_dict[selectedLocation]["latitude"],
        lon=locations_dict[selectedLocation]["longitude"]
    )

    if not wave_forecast:
        raise ValueError("Failed to get forecast from NOAA")

    return wave_forecast


@app.route("/", methods=["GET", "POST"])
def location_selection():
    return render_template("index.html", locations=locations_dict.keys())


@app.route("/forecast.html", methods=["GET", "POST"])
def wave_forecast():
    selectedLocation = request.form.get("location")
    
    data = generate_wave_forecast(selectedLocation)
    plot_image = data[0]
    wave_height = data[1]

    return render_template(
        "forecast.html",
        location=selectedLocation,
        plot_url=plot_image,
        current_wave_height=wave_height,
        locations=locations_dict.keys(),
        selectedLocation=selectedLocation,
    )


if __name__ == "__main__":
    app.run(debug=True)
