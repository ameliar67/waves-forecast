import json
from datetime import timedelta

from cache import Cache
from config import app_session


def get_location_country(latitude: str, longitude: str, cache: Cache) -> str | None:
    response_data = reverse_geocode(latitude, longitude, cache)
    try:
        return response_data["features"][0]["properties"]["address"]["country"]
    except KeyError:
        return None


def reverse_geocode(latitude: str, longitude: str, cache: Cache) -> str | None:
    cache_key = f"geocode/v1/{latitude},{longitude}"
    cache_encoding = "utf-8"

    cache_item = cache.get_item(cache_key, max_age=timedelta(weeks=52))
    if cache_item is not None:
        return json.loads(cache_item.decode(cache_encoding))

    url = f"https://nominatim.openstreetmap.org/reverse?format=geojson&lat={latitude}&lon={longitude}"
    reverse_geo_response = app_session.get(url)

    if not reverse_geo_response.ok:
        raise Exception(
            f"Geocode request failed with status {reverse_geo_response.status_code}"
        )

    cache.set_item(cache_key, reverse_geo_response.text.encode(cache_encoding))
    return json.loads(reverse_geo_response.text)
