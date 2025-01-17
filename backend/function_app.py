import json

import azure.functions as func
import surf_data
import surfpy
from azure.identity import DefaultAzureCredential
from azure.storage.blob import ContainerClient
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

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.function_name(name="LocationsList")
@app.route(route="locations", methods=["GET"])
def home_page(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        json.dumps({"locations": locations_dict}),
        mimetype="application/json",
        status_code=200,
        headers={"Cache-Control": "public, max-age=7200"},
    )


@app.function_name(name="LocationForecast")
@app.route(route="forecast/{location_id}", methods=["GET"])
def forecast(req: func.HttpRequest) -> func.HttpResponse:
    location_id = req.route_params.get("location_id")
    if location_id not in locations_dict:
        error = f"No location matching {location_id}, is currently available"
        return func.HttpResponse(error, status_code=404)

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
        # TODO - return error response
        raise ValueError("Failed to get forecast from NOAA")

    response_data = {
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
        "wind_direction": wave_forecast["wind_direction"],
    }

    return func.HttpResponse(
        json.dumps(response_data),
        mimetype="application/json",
        status_code=200,
        headers={"Cache-Control": "public, max-age=1800"},
    )
