def filterLocations(buoyStations) -> dict:

    buoyStations.fetch_stations()

    locations_dict = {}

    for buoyStation in buoyStations.stations:
        if (
            buoyStation.buoy_type == "tao"
            or buoyStation.buoy_type == "oilrig"
            or buoyStation.buoy_type == "dart"
            or buoyStation.owner == "Prediction and Research Moored Array in the Atlantic"
        ):
            continue
        locations_dict[buoyStation.location.name] = {
            "longitude": float(buoyStation.location.longitude),
            "latitude": float(buoyStation.location.latitude),
        }

    return locations_dict