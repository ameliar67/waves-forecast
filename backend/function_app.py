import json
import logging

import azure.functions as func
import forecast_data
from azure.storage.blob import ContentSettings
from azurefunctions.extensions.bindings.blob import BlobClient
from locations import get_coastal_locations
from wave_model import get_wave_model

data_container_name = "data"
locations_blob_path = f"{data_container_name}/locations"

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.function_name("RefreshLocations")
@app.timer_trigger(schedule="15 3 * * *", run_on_startup=False, arg_name="timer")
@app.blob_input(arg_name="locationsblob", path=locations_blob_path, connection="")
async def refresh_locations(timer: func.TimerRequest, locationsblob: BlobClient):
    logging.info("Refreshing locations response blob")

    # Get updated locations and upload to Blob storage
    locations_data = get_coastal_locations()
    response_content = json.dumps({"locations": locations_data})

    content_settings = ContentSettings(
        content_type="application/json", cache_control="public, max-age=7200"
    )
    locationsblob.upload_blob(
        response_content, overwrite=True, content_settings=content_settings
    )
