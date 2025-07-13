import json
import logging
import os
from typing import TypedDict

import forecast_calculation as forecast_calculation
from azure.storage.blob import BlobClient, ContainerClient, ContentSettings
from locations import get_coastal_locations
from wave_model import get_wave_model

IS_DEVELOPMENT_MODE = os.environ.get("IS_DEVELOPMENT") in ("1", "True", "true")
data_container_name = "data"
locations_blob_path = f"{data_container_name}/locations"


class LocationForecastRequest(TypedDict):
    output_path: str
    name: str
    buoy_latitude: float
    buoy_longitude: float
    beach_latitude: float
    beach_longitude: float
    tide_stations: list
    jetty_obstructions: list


async def refresh_forecast(
    location: LocationForecastRequest, data_container_client: ContainerClient
) -> None:
    logging.info("Refreshing forecast for %s", location["name"])

    # Determine NOAA wave model
    wave_model = get_wave_model(location["buoy_latitude"], location["buoy_longitude"])
    # Fetch wave forecast data
    wave_forecast = await forecast_calculation.get_wave_forecast(
        wave_model=wave_model,
        buoy_lat=location["buoy_latitude"],
        buoy_lon=location["buoy_longitude"],
        tide_stations=location["tide_stations"],
        beach_lat=location["beach_latitude"],
        beach_lon=location["beach_longitude"],
        jetty_obstructions=location["jetty_obstructions"],
    )

    # Handle missing forecast data
    if not wave_forecast:
        logging.error("Failed to retrieve forecast data for %s", location["name"])
        return

    # Prepare response data
    wave_forecast["selected_location"] = location["name"]

    forecast_blob_client = data_container_client.get_blob_client(
        location["output_path"]
    )
    content_settings = ContentSettings(
        content_type="application/json", cache_control="public, max-age=1800"
    )
    forecast_blob_client.upload_blob(
        json.dumps(wave_forecast), overwrite=True, content_settings=content_settings
    )


async def refresh_api_data(locations_blob: BlobClient):
    logging.info("Refreshing locations response blob")

    # Get updated locations and upload to Blob storage
    locations_data = get_coastal_locations()
    response_content = json.dumps({"locations": locations_data})

    content_settings = ContentSettings(
        content_type="application/json", cache_control="public, max-age=7200"
    )
    locations_blob.upload_blob(
        response_content, overwrite=True, content_settings=content_settings
    )

    logging.info("Refreshing forecasts for locations")
    for loc in locations_data.values():
        try:
            await refresh_forecast(
                {
                    "output_path": f"forecast/{loc['id']}",
                    "buoy_latitude": loc["buoy_latitude"],
                    "buoy_longitude": loc["buoy_longitude"],
                    "name": loc["name"],
                    "tide_stations": loc["tide_stations"],
                    "beach_latitude": loc["beach_latitude"],
                    "beach_longitude": loc["beach_longitude"],
                    "jetty_obstructions": loc["jetty_obstructions"],
                },
                None,
            )
        except Exception:
            logging.error(
                "Error while generating forecast for %s", loc["name"], exc_info=True
            )

        if IS_DEVELOPMENT_MODE:
            # Only process a single location in development
            break
