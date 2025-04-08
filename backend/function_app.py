import json
import logging
import os
from typing import TypedDict

import azure.functions as func
import forecast_data
from azure.storage.blob import BlobClient, ContainerClient, ContentSettings
import azurefunctions.extensions.bindings.blob as blob_binding
from locations import LocationData, get_coastal_locations
from wave_model import get_wave_model

IS_DEVELOPMENT_MODE = os.environ.get("IS_DEVELOPMENT") in ("1", "True", "true")
data_container_name = "data"
locations_blob_path = f"{data_container_name}/locations"
refresh_forecast_queue_name = "refresh-forecast"

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


class ForecastQueueMessage(TypedDict):
    output_path: str
    name: str
    lat: float
    long: float


@app.function_name("LocationForecast")
@app.queue_trigger(
    arg_name="message", queue_name=refresh_forecast_queue_name, connection=""
)
@app.blob_input(
    arg_name="datacontainer",
    path=data_container_name,
    connection="",
)
async def forecast(message: str, datacontainer: blob_binding.ContainerClient) -> None:
    logging.info("Refreshing forecast for %s", message)
    # Convert type hint from blob binding (required by Azure Functions) to normal ContainerClient (code completion)
    data_container_client: ContainerClient = datacontainer
    selected_location: ForecastQueueMessage = json.loads(message)

    # Fetch wave forecast data
    wave_model = get_wave_model(
        selected_location["latitude"], selected_location["longitude"]
    )
    wave_forecast = await forecast_data.get_wave_forecast(
        wave_model=wave_model,
        lat=selected_location["latitude"],
        lon=selected_location["longitude"],
    )

    # Handle missing forecast data
    if not wave_forecast:
        logging.error("Failed to retrieve forecast data for %s", message)
        return

    # Prepare response data
    wave_forecast["selected_location"] = selected_location["name"]

    forecast_blob_client = data_container_client.get_blob_client(
        selected_location["output_path"]
    )
    content_settings = ContentSettings(
        content_type="application/json", cache_control="public, max-age=1800"
    )
    forecast_blob_client.upload_blob(
        json.dumps(wave_forecast), overwrite=True, content_settings=content_settings
    )


@app.function_name("RefreshLocations")
@app.timer_trigger(schedule="15 3 * * *", run_on_startup=False, arg_name="timer")
@app.blob_input(arg_name="locationsblob", path=locations_blob_path, connection="")
def refresh_locations(timer: func.TimerRequest, locationsblob: blob_binding.BlobClient):
    logging.info("Refreshing locations response blob")

    # Get updated locations and upload to Blob storage
    locations_data = get_coastal_locations()
    response_content = json.dumps({"locations": locations_data})

    # Convert type hint from blob binding (required by Azure Functions) to normal BlobClient (code completion)
    locations_blob: BlobClient = locationsblob
    content_settings = ContentSettings(
        content_type="application/json", cache_control="public, max-age=7200"
    )
    locations_blob.upload_blob(
        response_content, overwrite=True, content_settings=content_settings
    )


@app.function_name("QueueLocationForecasts")
@app.timer_trigger(schedule="15 4 * * *", run_on_startup=False, arg_name="timer")
@app.blob_input(
    arg_name="locationsjson",
    path=locations_blob_path,
    connection="",
    data_type="string",
)
@app.queue_output(
    arg_name="$return", queue_name=refresh_forecast_queue_name, connection=""
)
def queue_location_forecasts(timer: func.TimerRequest, locationsjson: str):
    locations: dict[str, LocationData] = json.loads(locationsjson)["locations"]
    queue_messages: list[str] = []

    for loc in locations.values():
        message: ForecastQueueMessage = {
            "output_path": f"forecast/{loc['id']}",
            "latitude": loc["latitude"],
            "longitude": loc["longitude"],
            "name": loc["name"],
        }
        queue_messages.append(json.dumps(message))

    if IS_DEVELOPMENT_MODE:
        # Only queue a single message in development
        queue_messages = queue_messages[:1]

    return queue_messages
