import surfpy
import datetime
from typing import Literal, TypedDict
import json


class KnownLocation(TypedDict):
    name: str
    state: str


class LocationData(TypedDict):
    id: str
    name: str
    longitude: float
    latitude: float
    tide_data: object


def getTide() -> dict[str, LocationData]:
    tide_stations = surfpy.TideStations()
    tide_stations.fetch_stations()

    start_date = datetime.datetime.today()
    end_date = start_date + datetime.timedelta(days=2)

    tide_locations_dict = {}
    with open("known_locations.json") as fp:
        known_locations: dict[str, KnownLocation] = json.load(fp)

    # locations_with_less_lat_lon_precision = {}

    # # adjust keys to have lower lat lon precision to enable a tide station is included for the location
    # update_dict_keys(known_locations, locations_with_less_lat_lon_precision)

    # calculate closest station for each known location
    for station in tide_stations.stations:

        data_available, surf_location = is_tide_station_data_available(
            station, known_locations
        )
        if not data_available:
            continue
        known_locations[surf_location][
            "closest_tide_station"
        ] = station

    # fetch tide data for each closest tide station
    for location in known_locations.values():
        tide_station = location.get("closest_tide_station")
        if not tide_station:
            continue

        tide_data = tide_station.fetch_tide_data(
            start_date,
            end_date,
            interval=surfpy.TideStation.DataInterval.high_low,
            unit=surfpy.units.Units.metric,
        )

        if tide_data:
            print(location.get("name" or "Unknown"))

        # tide_data[0][i].date, tide_data[0][i].tidal_event

        tide_locations_dict[tide_station.station_id] = {
            "id": tide_station.station_id,
            "name": location.get("name" or "Unknown"),
            "longitude": float(tide_station.location.longitude),
            "latitude": float(tide_station.location.latitude),
            "tide_data": tide_data,
        }

    # print("tides", tide_locations_dict)


def is_tide_station_data_available(
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


def update_dict_keys(old_dict, new_dict):

    # adjust keys to have lower lat lon precision to enable a tide station is included for the location
    for key, value in old_dict.items():
        if len(key) >= 4:
            # Remove 3rd and 4th characters (index 2 and 3) and the last two characters
            new_key = key[:2] + key[4:-2]
        elif len(key) > 2:
            # If key is too short to have 3rd and 4th characters, just remove last 2
            new_key = key[:-2]
        else:
            new_key = key  # Leave it unchanged if too short
        new_dict[new_key] = value

    return new_dict
