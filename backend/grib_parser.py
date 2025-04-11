import logging
import struct
from collections.abc import Callable

import pygrib
import surfpy

# Set up logging for the GribParser class
logging.basicConfig(level=logging.INFO)

GRIB_START = "GRIB".encode("ascii")


class GribTimeWindow:
    def __init__(self):
        self.time = ""
        # location, resolution
        self.data_funcs: dict[str, Callable[[surfpy.Location, float], float]] = {}


def wrap_data_func(data_func) -> float:
    def get_result(location: surfpy.Location, location_resolution: float):
        rawvalue, _, _ = data_func(
            lat1=location.latitude - location_resolution,
            lat2=location.latitude + location_resolution,
            lon1=location.absolute_longitude - location_resolution,
            lon2=location.absolute_longitude + location_resolution,
        )

        return rawvalue.mean().item()

    return get_result


def parse_grib_data(raw_data: bytes) -> GribTimeWindow | None:
    if not pygrib or not raw_data or not len(raw_data):
        return None

    has_grib_data = False
    search_from = 0
    result = GribTimeWindow()

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
            result.time = message.validDate

        has_grib_data = True
        name = message.shortName

        if message.has_key("level"):
            if message.level > 1:
                name += "_" + str(message.level)

        result.data_funcs[name] = wrap_data_func(message.data)

    return result if has_grib_data else None
