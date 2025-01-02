def filterLocations(stations) -> dict:
    locations_dict = {}
    for buoyStation in stations:
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

    return locations_dict
