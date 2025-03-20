import json
import logging

import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContentSettings, PublicAccess
from cache import Cache
from config import Config
from locations import get_coastal_locations
from wave_model import get_wave_model
import forecast_data  # Ensure this import is included for wave forecasting

app_config = Config.from_environment()


# Initialize BlobServiceClient and container clients
blob_service_client = BlobServiceClient(
    app_config.cache_blob_account_url, DefaultAzureCredential()
)
cache_container_client = blob_service_client.get_container_client("forecast-cache")
data_container_client = blob_service_client.get_container_client("data")

# Create containers if not exist (only for development)
if app_config.is_development:

    def create_container_if_not_exists(container_client, public_access=None):
        if not container_client.exists():
            container_client.create_container(public_access=public_access)

    create_container_if_not_exists(cache_container_client, PublicAccess.OFF)
    create_container_if_not_exists(data_container_client, PublicAccess.BLOB)

cache = Cache(cache_container_client)
locations_dict = get_coastal_locations(cache)

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.function_name(name="LocationForecast")
@app.route(route="forecast/{location_id}", methods=["GET"])
def forecast(req: func.HttpRequest) -> func.HttpResponse:
    location_id = req.route_params.get("location_id")

    # Early return if location is not available
    selected_location = locations_dict.get(location_id)
    if not selected_location:
        error_message = f"No location matching {location_id}, is currently available"
        return func.HttpResponse(error_message, status_code=404)

    # Fetch wave forecast data
    wave_model = get_wave_model(
        selected_location["latitude"], selected_location["longitude"]
    )
    wave_forecast = forecast_data.get_wave_forecast(
        wave_model=wave_model,
        cache=cache,
        location_id=location_id,
        selected_location=selected_location["name"],
        lat=selected_location["latitude"],
        lon=selected_location["longitude"],
    )

    # Handle missing forecast data
    if not wave_forecast:
        logging.error(f"Failed to retrieve forecast data for {location_id}")
        return func.HttpResponse("Failed to retrieve forecast data", status_code=500)

    # Prepare response data
    response_data = {
        "selected_location": selected_location["name"],
        "current_wave_height": wave_forecast["average_wave_height"],
        "weather_alerts": wave_forecast["weather_alerts"],
        "air_temperature": wave_forecast["air_temperature"],
        "short_forecast": wave_forecast["short_forecast"],
        "wind_speed": wave_forecast["wind_speed"],
        "wind_direction": wave_forecast["wind_direction"],
        "hourly_forecast": wave_forecast["hourly_forecast"],
    }

    return func.HttpResponse(
        json.dumps(response_data),
        mimetype="application/json",
        status_code=200,
        headers={"Cache-Control": "public, max-age=1800"},
    )


@app.function_name("RefreshLocations")
@app.timer_trigger(schedule="15 3 * * *", run_on_startup=False, arg_name="timer")
def refresh_locations(timer: func.TimerRequest) -> None:
    logging.info("Refreshing locations cache entry and response blob")

    # Get updated locations and upload to Blob storage
    locations_data = get_coastal_locations(cache, force_refresh=True)
    response_content = json.dumps({"locations": locations_data}).encode("utf-8")

    locations_blob = data_container_client.get_blob_client("locations")
    content_settings = ContentSettings(
        content_type="application/json", cache_control="public, max-age=7200"
    )
    locations_blob.upload_blob(
        response_content, overwrite=True, content_settings=content_settings
    )
