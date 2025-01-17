import datetime
import json

import surfpy

from cache import Cache


def get_coastal_locations(cache: Cache):

    key = "buoy_locations/v1"
    cache_encoding = "utf-8"

    # check cache
    cache_item = cache.get_item(key, datetime.timedelta(days=1))
    # on hit: return
    if cache_item is not None:
        locations_dict = json.loads(cache_item.decode(cache_encoding))
        return locations_dict

    # on miss
    buoy_stations = surfpy.BuoyStations()
    buoy_stations.fetch_stations()

    locations_dict = {}
    for buoyStation in buoy_stations.stations:
        if (
            buoyStation.buoy_type in ("tao", "oilrig", "dart")
            or buoyStation.owner
            == "Prediction and Research Moored Array in the Atlantic"
            or not buoyStation.location.name
        ):
            continue
        locations_dict[buoyStation.station_id] = {
            "name": buoyStation.location.name,
            "longitude": float(buoyStation.location.longitude),
            "latitude": float(buoyStation.location.latitude),
        }

    # set cache
    cache.set_item(key, json.dumps(locations_dict).encode(cache_encoding))

    return locations_dict
