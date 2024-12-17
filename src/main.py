import surf_data
import surfpy
import xml.etree.ElementTree as ET
from cache import Cache
import os
from starlette.applications import Starlette
from starlette.templating import Jinja2Templates
from starlette.responses import HTMLResponse
from starlette.requests import Request
from starlette.routing import Route

templates = Jinja2Templates(directory="templates")

path = os.path.dirname(os.path.abspath(__file__))
db = os.path.join(path, "database.db")

cache = Cache(db)
cache.migrate()

locations_dict = {}

tree = ET.parse(
    os.path.join(path, "../libs/surfpy/surfpy/tests/data/activestations.xml")
)
root = tree.getroot()
for child in root:
    locations_dict[child.attrib["name"]] = {
        "id": child.attrib["id"],
        "longitude": float(child.attrib["lon"]),
        "latitude": float(child.attrib["lat"]),
    }


def generate_wave_forecast(selected_location):

    wave_forecast = surf_data.get_wave_forecast(
        wave_model=surfpy.wavemodel.us_west_coast_gfs_wave_model(),
        cache=cache,
        selectedLocation=selected_location,
        lat=locations_dict[selected_location]["latitude"],
        lon=locations_dict[selected_location]["longitude"],
    )

    if not wave_forecast:
        raise ValueError("Failed to get forecast from NOAA")

    return wave_forecast


async def landing_page(request):

    context = {"request": request, "locations": locations_dict.keys()}

    return templates.TemplateResponse("index.html", context)


async def forecast(request: Request):
    form_data = await request.form()
    selected_location = form_data.get("location-list")
    plot_image = generate_wave_forecast(selected_location)

    try:

        context = {
            "request": request,
            "locations": locations_dict.keys(),
            "plot_url": plot_image,
            "location": selected_location,
        }

        return templates.TemplateResponse("forecast.html", context)

    except Exception as e:
        context = {"request": request, "error": e}

        return templates.TemplateResponse("404.html", context)


routes = [
    Route("/", landing_page),
    Route("/forecast.html", forecast, methods=["POST"]),
]

app = Starlette(debug=True, routes=routes)
