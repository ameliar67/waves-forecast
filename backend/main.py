import surfpy
from azure.identity import DefaultAzureCredential
from azure.storage.blob import ContainerClient
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

import surf_data
from cache import Cache
from config import Config
from locations import get_coastal_locations

app_config = Config.from_environment()

cache_container_client = ContainerClient(
    app_config.cache_blob_account_url,
    "forecast-cache",
    DefaultAzureCredential(),
)
cache = Cache(cache_container_client)

locations_dict = get_coastal_locations(cache)


async def landing_page(request):
    return JSONResponse({
        "locations": locations_dict,
    })


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
        "wave_height_graph": wave_forecast["chart"],
        "selected_location": selected_location["name"],
        "current_wave_height": wave_forecast["average_wave_height"],
        "units": surfpy.units.unit_name(
            surfpy.units.Units.metric, surfpy.units.Measurement.length
        ),
        "weather_alerts": wave_forecast["weather_alerts"],
        "air_temperature": wave_forecast["air_temperature"],
        "short_forecast": wave_forecast["short_forecast"],
        "wind_speed": wave_forecast["wind_speed"],
        "wind_direction": wave_forecast["wind_direction"]
    }

    return JSONResponse(context)


async def not_found(request: Request, exc: HTTPException):
    return JSONResponse({
        "detail": exc.detail or "The page you are looking for could not be found.",
        "status_code": exc.status_code
    }, status_code=exc.status_code)

# General error handler for other HTTP exceptions (e.g. 500, 400)
async def server_error(request: Request, exc: HTTPException):
    return JSONResponse({
        "detail": exc.detail or "Internal server error.",
        "status_code": exc.status_code
    }, status_code=exc.status_code)

# General error handler for all other HTTP exceptions
async def handle_error(request: Request, exc: HTTPException):
    return JSONResponse({
        "detail": exc.detail or "An error occurred.",
    }, status_code=exc.status_code)


routes = [
    Route("/locations", landing_page),
    Route("/forecast/{location_id:str}", forecast, methods=["GET"]),
]

exception_handlers = {404: not_found, 500: server_error, Exception: handle_error}

app = Starlette(routes=routes, exception_handlers=exception_handlers)
