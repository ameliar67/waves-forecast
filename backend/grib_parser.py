import logging
import pygrib
import struct
from io import BytesIO


# Set up logging for the GribParser class
logging.basicConfig(level=logging.INFO)


def parse_grib_data(location, raw_data, location_resolution, data={}):
    if not pygrib:
        return None
    if not raw_data:
        return None
    elif not len(raw_data):
        return None

    f = BytesIO(raw_data)
    raw_messages = []

    # Profile the loop for finding GRIB messages
    while 1:
        nbyte = f.tell()
        while 1:
            f.seek(nbyte)
            start = f.read(4)
            sstart = start.decode("ascii", errors="ignore")
            if sstart == "" or sstart == "GRIB":
                break
            nbyte = nbyte + 1

        if sstart == "":
            break
        startpos = f.tell() - 4
        f.read(4)  # next four octets are reserved
        lengrib = struct.unpack(">q", f.read(8))[0]
        f.seek(startpos)
        gribmsg = f.read(lengrib)
        raw_messages.append(gribmsg)

    # Profiling data collection for GRIB message processing
    first_time_string = pygrib.fromstring(raw_messages[0])

    if not first_time_string:
        return None

    # Parse out the timestamp first
    if data.get("time") is None:
        data["time"] = [first_time_string.validDate]
    else:
        data["time"].append(first_time_string.validDate)

    # Now profile the loop for processing each GRIB message
    for m in raw_messages:
        message = pygrib.fromstring(m)

        if not message:
            continue

        name = message.shortName

        if message.has_key("level"):
            if message.level > 1:
                name += "_" + str(message.level)

        rawvalue, lats, lons = message.data(
            lat1=location.latitude - location_resolution,
            lat2=location.latitude + location_resolution,
            lon1=location.absolute_longitude - location_resolution,
            lon2=location.absolute_longitude + location_resolution,
        )

        value = rawvalue.mean().item()

        if data.get(name) is None:
            data[name] = [value]
        else:
            data[name].append(value)

    if not len(raw_messages):
        return None

    return data
