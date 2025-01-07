import os

import surfpy
from azure.identity import DefaultAzureCredential
from azure.storage.blob import ContainerClient
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

import map
import surf_data
from cache import Cache
from config import Config
from locations import get_coastal_locations

templates = Jinja2Templates(directory="templates")

app_root_path = os.path.dirname(os.path.abspath(__file__))
app_config = Config.from_environment()

cache_container_client = ContainerClient(
    app_config.cache_blob_account_url,
    "forecast-cache",
    DefaultAzureCredential(),
)
cache = Cache(cache_container_client)

locations_dict = get_coastal_locations(cache)


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
        error = f"No location matching {location_id}, is currently available"
        return await not_found(request, HTTPException(404, error))

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
        "air_temperature": wave_forecast["air_temperature"]
    }

    return templates.TemplateResponse("forecast.html", context)


async def not_found(request: Request, exc: HTTPException):
     return templates.TemplateResponse("404.html", {"request": request, "detail": exc.detail, "status_code": exc.status_code})


async def server_error(request: Request, exc: HTTPException):
     return templates.TemplateResponse("500.html", {"request": request, "detail": exc.detail, "status_code": exc.status_code})


async def handle_error(request: Request, exc: HTTPException):
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)


routes = [
    Route("/", landing_page),
    Mount("/templates", app=StaticFiles(directory="templates"), name="html_templates"),
    Route("/forecast/{location_id:str}", forecast, methods=["GET"]),
    Mount("/static", app=StaticFiles(directory="static"), name="static"),
]

exception_handlers = {404: not_found, 500: server_error, Exception: handle_error}

app = Starlette(debug=True, routes=routes, exception_handlers=exception_handlers)
