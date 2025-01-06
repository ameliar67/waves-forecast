import os

import surfpy
from azure.identity import DefaultAzureCredential
from azure.storage.blob import ContainerClient
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

import map
import surf_data
from cache import Cache
from locations import get_coastal_locations

templates = Jinja2Templates(directory="templates")

path = os.path.dirname(os.path.abspath(__file__))

cache_container_client = ContainerClient(
    "https://localhost:10000/devstoreaccount1",  # TODO: read from environment/configuration
    "forecast-cache",
    DefaultAzureCredential(),
)
cache = Cache(cache_container_client)

locations_dict = get_coastal_locations(cache)

HTML_404_PAGE = os.path.join(path, "../templates/404.html")
HTML_500_PAGE = os.path.join(path, "../templates/500.html")


async def landing_page(request):

    world_map = map.generate_map(locations_dict)
    context = {
        "request": request,
        "locations": locations_dict,
        "world_map": world_map,
    }
    return templates.TemplateResponse("index.html", context)


async def forecast(request: Request):
    location_id = request.path_params.get("location_id")
    if location_id not in locations_dict:
        # TODO - return an error message
        return not_found()

    selected_location = locations_dict[location_id]
    wave_forecast = surf_data.get_wave_forecast(
        wave_model=surfpy.wavemodel.us_west_coast_gfs_wave_model(),
        cache=cache,
        location_id=location_id,
        selected_location=selected_location["name"],
        lat=selected_location["latitude"],
        lon=selected_location["longitude"],
    )

    if not wave_forecast:
        raise ValueError("Failed to get forecast from NOAA")

    context = {
        "request": request,
        "locations": locations_dict,
        "wave_height_graph": wave_forecast["chart"],
        "selected_location": selected_location["name"],
        "current_wave_height": wave_forecast["average_wave_height"],
        "units": surfpy.units.unit_name(
            surfpy.units.Units.metric, surfpy.units.Measurement.length
        ),
        "weather_alerts": wave_forecast["weather_alerts"],
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
    Route("/forecast/{location_id:str}", forecast, methods=["GET"]),
    Mount("/static", app=StaticFiles(directory="static"), name="static"),
]

exception_handlers = {404: not_found, 500: server_error, Exception: handle_error}

app = Starlette(debug=True, routes=routes, exception_handlers=exception_handlers)
