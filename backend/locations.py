import json
from typing import Literal, TypedDict

import surfpy


class KnownLocation(TypedDict):
    name: str
    state: str


class LocationData(TypedDict):
    id: str
    name: str
    longitude: float
    latitude: float
    country: str
    state: str
    tide_station: str


def is_in_great_lakes_region(lat, lon):
    lon = lon if lon >= 0 else lon + 360
    return 41.0 <= lat <= 49.0 and 267.5 <= lon <= 285.0


def get_coastal_locations() -> dict[str, LocationData]:

    # fetch NOAA station data for buoy and tide stations (they are seperate)

    buoy_stations = surfpy.BuoyStations()
    buoy_stations.fetch_stations()

    tide_stations = surfpy.TideStations()
    tide_stations.fetch_stations()

    # calculate closest buoy station

    locations_dict = {}
    with open("known_locations.json") as fp:
        known_locations: dict[str, KnownLocation] = json.load(fp)

    for buoyStation in buoy_stations.stations:
        data_available, surf_location = is_buoy_data_available(
            buoyStation, known_locations, 1
        )
        if not data_available or is_in_great_lakes_region(
            buoyStation.location.latitude, buoyStation.location.longitude
        ):
            continue
        known_locations[surf_location]["closest_station"] = buoyStation

    # calculate closest tide station

    adjusted_known_locations = round_dict_keys_by_precision(known_locations, 0)

    for tideStation in tide_stations.stations:
        data_available, surf_location = is_buoy_data_available(
            tideStation, adjusted_known_locations, 0
        )
        if not data_available:
            continue
        adjusted_known_locations[surf_location][
            "closest_tide_station"
        ] = tideStation.station_id

    for location in adjusted_known_locations.values():
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
            "tide_station": location.get("closest_tide_station") or None,
        }

    return locations_dict


def is_buoy_data_available(
    station: surfpy.BuoyStation, known_locations: object, rounding_precision: int
) -> tuple[Literal[False], None] | tuple[Literal[True], str]:

    rounded_lat = round(station.location.latitude, rounding_precision)
    rounded_lon = round(station.location.longitude, rounding_precision)
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


def round_dict_keys_by_precision(data: dict, precision: int) -> dict:
    """
    Takes a dictionary where keys are strings of the form 'lat,lon',
    rounds the float values of lat and lon to the given precision,
    and returns a new dictionary with the rounded keys.


    """
    new_dict = {}
    for key, value in data.items():
        try:
            lat_str, lon_str = key.split(",")
            lat = round(float(lat_str), precision)
            lon = round(float(lon_str), precision)
            new_key = f"{lat},{lon}"
            new_dict[new_key] = value
        except ValueError:
            raise ValueError(f"Invalid key format: {key}. Expected format 'lat,lon'.")
    return new_dict
