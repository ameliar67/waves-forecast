import json
import logging
from typing import TypedDict

import forecast_calculation
from config import Config
from context import ForecastContext
from locations import get_coastal_locations
from wave_model import get_wave_model

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
    config: Config, context: ForecastContext, location: LocationForecastRequest
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

    # Upload to S3
    config.s3_bucket.put_object(
        Key=location["output_path"],
        Body=json.dumps(wave_forecast),
        ContentType="application/json",
        CacheControl="public, max-age=1800",
    )


async def refresh_api_data(config: Config):
    async with ForecastContext() as context:
        logging.info("Refreshing locations response blob")

        # Get updated locations and upload to S3
        locations_data = get_coastal_locations(context)
        config.s3_bucket.put_object(
            Key=locations_blob_path,
            Body=json.dumps({"locations": locations_data}),
            ContentType="application/json",
            CacheControl="public, max-age=7200",
        )

        logging.info("Refreshing forecasts for locations")
        for loc in locations_data.values():
            try:
                await refresh_forecast(
                    config,
                    context,
                    {
                        "output_path": f"{data_container_name}/forecast/{loc['id']}",
                        "buoy_latitude": loc["buoy_latitude"],
                        "buoy_longitude": loc["buoy_longitude"],
                        "name": loc["name"],
                        "tide_stations": loc["tide_stations"],
                        "beach_latitude": loc["beach_latitude"],
                        "beach_longitude": loc["beach_longitude"],
                        "jetty_obstructions": loc["jetty_obstructions"],
                    },
                )
            except Exception:
                logging.exception("Error while generating forecast for %s", loc["name"])

            if config.is_development:
                # Only process a single location in development
                break
