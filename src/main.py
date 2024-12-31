import surf_data
import map
import surfpy
import filteredLocations
import xml.etree.ElementTree as ET
from cache import Cache
import os
from starlette.applications import Starlette
from starlette.templating import Jinja2Templates
from starlette.requests import Request
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.responses import HTMLResponse, JSONResponse
from starlette.exceptions import HTTPException

templates = Jinja2Templates(directory="templates")

path = os.path.dirname(os.path.abspath(__file__))
db = os.path.join(path, "database.db")

cache = Cache(db)
cache.migrate()

locations_dict = filteredLocations.filterLocations(surfpy.BuoyStations())

HTML_404_PAGE = os.path.join(path, "../templates/404.html")
HTML_500_PAGE = os.path.join(path, "../templates/500.html")


def generate_wave_forecast(selected_location):

    wave_forecast = surf_data.get_wave_forecast(
        wave_model=surfpy.wavemodel.us_west_coast_gfs_wave_model(),
        cache=cache,
        selected_location=selected_location,
        lat=locations_dict[selected_location]["latitude"],
        lon=locations_dict[selected_location]["longitude"],
    )

    if not wave_forecast:
        raise ValueError("Failed to get forecast from NOAA")

    return wave_forecast


async def landing_page(request):

    worldMap = map.generate_map()
    context = {
        "request": request,
        "locations": locations_dict.keys(),
        "world_map": worldMap,
    }
    return templates.TemplateResponse("index.html", context)


async def forecast(request: Request):
    form_data = await request.form()
    selected_location = form_data.get("location-list")

    data = generate_wave_forecast(selected_location)

    context = {
        "request": request,
        "locations": locations_dict.keys(),
        "wave_height_graph": data.chart,
        "selected_location": selected_location,
        "current_wave_height": data.wave_height,
        "units": surfpy.units.unit_name(
            surfpy.units.Units.metric, surfpy.units.Measurement.length
        ),
        "weather_alerts": data.alerts,
    }

    return templates.TemplateResponse("forecast.html", context)


async def not_found(request: Request, exc: HTTPException):
    return HTMLResponse(content=HTML_404_PAGE, status_code=exc.status_code)


async def server_error(request: Request, exc: HTTPException):
    return HTMLResponse(content=HTML_500_PAGE, status_code=exc.status_code)


async def handle_error(request: Request, exc: HTTPException):
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)


routes = [
    Route("/", landing_page),
    Mount("/templates", app=StaticFiles(directory="templates"), name="template"),
    Route("/forecast.html", forecast, methods=["POST"]),
    Mount("/static", app=StaticFiles(directory="static"), name="static"),
]

exception_handlers = {404: not_found, 500: server_error, Exception: handle_error}

app = Starlette(debug=True, routes=routes, exception_handlers=exception_handlers)
