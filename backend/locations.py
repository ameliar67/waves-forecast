import json
from typing import Literal, TypedDict

import surfpy


class KnownLocation(TypedDict):
    name: str
    state: str


class LocationData(TypedDict):
    id: str
    name: str
    buoy_longitude: float
    buoy_latitude: float
    country: str
    state: str
    tide_stations: list
    beach_latitude: float
    beach_longitude: float
    jetty_obstructions: int


def get_coastal_locations() -> dict[str, LocationData]:

    # fetch NOAA station data for wave heights and tides (data comes from seperate stations)
    buoy_stations = surfpy.BuoyStations()
    buoy_stations.fetch_stations()

    current_tide_stations = surfpy.TideStations()
    current_tide_stations.fetch_stations()

    # calculate closest buoy station
    locations_dict = {}
    # open pre-estabilished list of known surfing locations
    with open("known_locations.json") as fp:
        known_surf_locations: dict[str, KnownLocation] = json.load(fp)

    for buoyStation in buoy_stations.stations:
        data_available, surf_location = get_closest_buoy_data_available(
            buoyStation, known_surf_locations, 1
        )
        if not data_available or is_in_great_lakes_region(
            buoyStation.location.latitude, buoyStation.location.longitude
        ):
            continue
        for beach_location in known_surf_locations[surf_location]:
            beach_location["closest_station"] = buoyStation

    for buoy_location in known_surf_locations.values():
        for beach_location in buoy_location:
            buoyStation = beach_location.get("closest_station")
            id = beach_location.get("id" or "Unknown")
            name = beach_location.get("name" or "Unknown")
            if not buoyStation:
                continue
            # calculate closest tide station
            closest_tide_stations = current_tide_stations.find_closest_stations(
                buoyStation.location, 2
            )
            buoy_name = get_buoy_display_name(buoyStation.location.name)

            tide_stations = [station.station_id for station in closest_tide_stations]

            # set country to United States until global buoys supported
            locations_dict[name] = {
                "id": id,
                "name": beach_location.get("name", buoy_name or "Unknown"),
                "buoy_longitude": float(buoyStation.location.longitude),
                "buoy_latitude": float(buoyStation.location.latitude),
                "country": "United States",
                "state": beach_location.get("state", "Unknown"),
                "tide_stations": tide_stations or None,
                "beach_latitude": beach_location.get("beach_latitude" or "Unknown"),
                "beach_longitude": beach_location.get("beach_longitude" or "Unknown"),
                "jetty_obstructions": beach_location.get("jetty_obstructions" or "Unknown"),
            }

    return locations_dict


def get_closest_buoy_data_available(
    station: surfpy.BuoyStation, known_surf_locations: object, rounding_precision: int
) -> tuple[Literal[False], None] | tuple[Literal[True], str]:

    rounded_lat = round(station.location.latitude, rounding_precision)
    rounded_lon = round(station.location.longitude, rounding_precision)
    lat_lon_key = f"{rounded_lat},{rounded_lon}"

    # Check if the key exists and calculate the difference
    location = known_surf_locations.get(lat_lon_key)
    if location:
        for entry in location:
            current_loc_diff = abs(station.location.latitude - rounded_lat) + abs(
                station.location.longitude - rounded_lon
            )
            closest_distance = entry.get("closest_distance")

            # Update and return if the current location is closer
            if closest_distance is None or closest_distance < current_loc_diff:
                entry["closest_distance"] = current_loc_diff
                return (True, lat_lon_key)

    # If the location is not found or no update is needed
    return (False, None)


def get_buoy_display_name(name: str) -> str:
    if len(name) > 4 and name[-4] == "," and name[-3] == " " and name[-2:].isupper():
        name = name[:-4]

    name = name.lstrip("0123456789- ").rstrip(", ")

    return name


def is_in_great_lakes_region(lat, lon):
    lon = lon if lon >= 0 else lon + 360
    return 41.0 <= lat <= 49.0 and 267.5 <= lon <= 285.0
