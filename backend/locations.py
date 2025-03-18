import datetime
import json
from typing import Literal, TypedDict

import surfpy
from cache import Cache


class KnownLocation(TypedDict):
    name: str
    state: str


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
    with open("known_locations.json") as fp:
        known_locations: dict[str, KnownLocation] = json.load(fp)

    for buoyStation in buoy_stations.stations:
        data_available, surf_location = is_buoy_data_available(
            buoyStation, known_locations
        )
        if not data_available:
            continue
        known_locations[surf_location]["closest_station"] = buoyStation

    for location in known_locations.values():
        buoyStation = location.get("closest_station")
        if not buoyStation:
            continue

        buoy_name = get_buoy_display_name(buoyStation.location.name)
        # set country to United States until global buoys supported
        locations_dict[buoyStation.station_id] = {
            "id": buoyStation.station_id,
            "name": location.get("name", buoy_name or "Unknown"),
            "longitude": float(buoyStation.location.longitude),
            "latitude": float(buoyStation.location.latitude),
            "country": "United States",
            "state": location.get("state", "Unknown"),
        }

    # set cache
    cache.set_item(key, json.dumps(locations_dict).encode(cache_encoding))

    return locations_dict


def is_buoy_data_available(
    station: surfpy.BuoyStation, known_locations: object
) -> tuple[Literal[False], None] | tuple[Literal[True], str]:

    rounded_lat = round(station.location.latitude, 1)
    rounded_lon = round(station.location.longitude, 1)
    lat_lon_key = f"{rounded_lat},{rounded_lon}"

    # Check if the key exists and calculate the difference
    location = known_locations.get(lat_lon_key)
    if location:
        current_loc_diff = abs(station.location.latitude - rounded_lat) + abs(
            station.location.longitude - rounded_lon
        )
        closest_distance = location.get("closest_distance")

        # Update and return if the current location is closer
        if closest_distance is None or closest_distance < current_loc_diff:
            location["closest_distance"] = current_loc_diff
            return (True, lat_lon_key)

    # If the location is not found or no update is needed
    return (False, None)


def get_buoy_display_name(name: str) -> str:
    if len(name) > 4 and name[-4] == "," and name[-3] == " " and name[-2:].isupper():
        name = name[:-4]

    name = name.lstrip("0123456789- ").rstrip(", ")

    return name
