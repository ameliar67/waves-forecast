import surfpy
from cache import Cache
from NOAA_data_retrieval import retrieve_new_data
import json
import datetime
import base64
from io import BytesIO

def get_wave_forecast(
    wave_model: str,
    cache: Cache,
    selectedLocation: surfpy.Location,
    lat=str,
    lon=str,
    hours_to_forecast=24,
) -> str:
    location = surfpy.Location(lat, lon, altitude=0, name=selectedLocation)
    location.depth = 10.0
    location.angle = 200.0
    location.slope = 0.28
    
    key = f"{location.name}"
    cache_item = cache.get_item(key)

    if cache_item is not None:
        # TODO: cache hit and miss paths should return an identical result
        # a caller should not observe a difference in behaviour (apart from latency) between cached vs fresh result
        result = json.loads(cache_item)
        return result

    image_data = retrieve_new_data(wave_model, hours_to_forecast, location)

    img = BytesIO()
    image_data.savefig(img, format="png")
    plot_base64_image = base64.b64encode(img.getvalue()).decode("utf8")

    expires_at = datetime.datetime.now().day + 1
    serialized_object = json.dumps(plot_base64_image)
    cache.set_item(key, serialized_object, expires_at)

    return plot_base64_image
