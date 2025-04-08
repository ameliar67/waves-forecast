import logging
import pygrib
import struct

import surfpy
from collections import defaultdict

# Set up logging for the GribParser class
logging.basicConfig(level=logging.INFO)

GRIB_START = "GRIB".encode("ascii")


def parse_grib_data(
    location: surfpy.Location,
    raw_data: bytes,
    location_resolution: float,
    data: defaultdict[str, list],
):
    if not pygrib or not raw_data or not len(raw_data):
        return None

    has_grib_data = False
    search_from = 0
    while True:
        startpos = raw_data.find(GRIB_START, search_from)
        if startpos == -1:
            # No more messages
            break

        lengrib = struct.unpack_from(
            ">q",
            buffer=raw_data,
            # Read length after skipping GRIB header + reserved 4 bytes
            offset=startpos + len(GRIB_START) + 4,
        )[0]
        search_from = startpos + lengrib

        message = pygrib.fromstring(raw_data[startpos : (startpos + lengrib)])
        if not message:
            continue

        if not has_grib_data:
            # Pull time from first grib message
            data["time"].append(message.validDate)

        has_grib_data = True
        name = message.shortName

        if message.has_key("level"):
            if message.level > 1:
                name += "_" + str(message.level)

        rawvalue, _, _ = message.data(
            lat1=location.latitude - location_resolution,
            lat2=location.latitude + location_resolution,
            lon1=location.absolute_longitude - location_resolution,
            lon2=location.absolute_longitude + location_resolution,
        )

        value = rawvalue.mean().item()
        data[name].append(value)

    return data if has_grib_data else None
