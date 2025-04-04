import json
import logging
from typing import TypedDict

import azure.functions as func
import forecast_data
from azure.storage.blob import BlobClient, ContainerClient, ContentSettings
import azurefunctions.extensions.bindings.blob as blob_binding
from config import IS_DEVELOPMENT_MODE
from locations import LocationData, get_coastal_locations
from wave_model import get_wave_model

data_container_name = "data"
locations_blob_path = f"{data_container_name}/locations"
refresh_forecast_queue_name = "refresh-forecast"

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.function_name("RefreshLocations")
@app.timer_trigger(schedule="15 3 * * *", run_on_startup=False, arg_name="timer")
@app.blob_input(arg_name="locationsblob", path=locations_blob_path, connection="")
async def refresh_locations(
    timer: func.TimerRequest, locationsblob: blob_binding.BlobClient
):
    logging.info("Refreshing locations response blob")
    # Convert type hint from blob binding (required by Azure Functions) to normal BlobClient (code completion)
    locationsblob: BlobClient = locationsblob

    # Get updated locations and upload to Blob storage
    locations_data = get_coastal_locations()
    response_content = json.dumps({"locations": locations_data})

    content_settings = ContentSettings(
        content_type="application/json", cache_control="public, max-age=7200"
    )
    locationsblob.upload_blob(
        response_content, overwrite=True, content_settings=content_settings
    )


class ForecastQueueMessage(TypedDict):
    output_path: str
    name: str
    lat: float
    long: float


@app.function_name("QueueRefreshForecasts")
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
async def queue_refresh_forecasts(timer: func.TimerRequest, locationsjson: str):
    locations: dict[str, LocationData] = json.loads(locationsjson)["locations"]
    queue_messages: list[str] = []

    for loc in locations.values():
        message: ForecastQueueMessage = {
            "output_path": f"forecast/{loc['id']}",
            "lat": loc["latitude"],
            "long": loc["longitude"],
            "name": loc["name"],
        }
        queue_messages.append(json.dumps(message))

    if IS_DEVELOPMENT_MODE:
        # Only queue a single message in development
        queue_messages = queue_messages[:1]

    return queue_messages


@app.function_name("RefreshLocationForecast")
@app.queue_trigger(
    arg_name="message", queue_name=refresh_forecast_queue_name, connection=""
)
@app.blob_input(
    arg_name="datacontainer",
    path=data_container_name,
    connection="",
)
async def refresh_location_forecast(
    message: str, datacontainer: blob_binding.ContainerClient
) -> None:
    logging.info(f"Refreshing forecast for {message}")
    # Convert type hint from blob binding (required by Azure Functions) to normal ContainerClient (code completion)
    datacontainer: ContainerClient = datacontainer
    location: ForecastQueueMessage = json.loads(message)

    wave_model = get_wave_model(location["lat"], location["long"])
    wave_forecast = await forecast_data.get_wave_forecast(
        wave_model=wave_model,
        lat=location["lat"],
        lon=location["long"],
    )

    if not wave_forecast:
        err_message = f"Failed to retrieve forecast data for {message}"
        logging.error(err_message)
        raise ValueError(err_message)

    response_content = json.dumps(
        {
            "selected_location": location["name"],
            "current_wave_height": wave_forecast["average_wave_height"],
            "weather_alerts": wave_forecast["weather_alerts"],
            "air_temperature": wave_forecast["air_temperature"],
            "short_forecast": wave_forecast["short_forecast"],
            "wind_speed": wave_forecast["wind_speed"],
            "wind_direction": wave_forecast["wind_direction"],
            "hourly_forecast": wave_forecast["hourly_forecast"],
        }
    )

    forecast_blob_client = datacontainer.get_blob_client(location["output_path"])
    content_settings = ContentSettings(
        content_type="application/json", cache_control="public, max-age=1800"
    )
    await forecast_blob_client.upload_blob(
        response_content, overwrite=True, content_settings=content_settings
    )
