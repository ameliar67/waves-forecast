import datetime
import json

import surfpy
from cache import Cache
from geocode import get_location_country, get_location_state


def get_coastal_locations(cache: Cache, force_refresh: bool = False):

    key = "ttl-short/buoy_locations/v1"
    cache_encoding = "utf-8"

    # check cache if not forcing refresh
    cache_item = (
        None if force_refresh else cache.get_item(key, datetime.timedelta(days=365))
    )

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
            or buoyStation.name == ""
        ):
            continue

        loc_country = get_location_country(
            buoyStation.location.latitude, buoyStation.location.longitude, cache=cache
        )

        loc_state = get_location_state(
            buoyStation.location.latitude, buoyStation.location.longitude, cache=cache
        )

        if loc_country != "United States" or loc_state is None:
            continue

        locations_dict[buoyStation.station_id] = {
            "id": buoyStation.station_id,
            "name": buoyStation.location.name,
            "longitude": float(buoyStation.location.longitude),
            "latitude": float(buoyStation.location.latitude),
            "country": loc_country,
            "state": loc_state or "Unknown",
        }

    # set cache
    cache.set_item(key, json.dumps(locations_dict).encode(cache_encoding))

    return locations_dict


def is_buoy_data_available(
    station: surfpy.BuoyStation,
    known_locations: object
) -> tuple[Literal[False], None] | tuple[Literal[True], str]:
    
    rounded_lat = round(station.location.latitude, 1)
    rounded_lon = round(station.location.longitude, 1)
    lat_lon_key = f"{rounded_lat},{rounded_lon}"

    # Check if the key exists and calculate the difference
    location = known_locations.get(lat_lon_key)
    if location:
        current_loc_diff = abs(station.location.latitude - rounded_lat) + abs(station.location.longitude - rounded_lon)
        closest_distance = location.get('closest_distance')

        # Update and return if the current location is closer
        if closest_distance is None or closest_distance < current_loc_diff:
            location['closest_distance'] = current_loc_diff
            return (True, lat_lon_key)

    # If the location is not found or no update is needed
    return (False, None)


def get_buoy_display_name(name: str) -> str:
    if len(name) > 4 and name[-4] == "," and name[-3] == " " and name[-2:].isupper():
        name = name[:-4]

    name = name.lstrip("0123456789- ").rstrip(", ")

    return name
