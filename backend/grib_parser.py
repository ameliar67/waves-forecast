import logging
import pygrib
import struct
from io import BytesIO


# Set up logging for the GribParser class
logging.basicConfig(level=logging.INFO)


class GribParser:

    def __init__(self, location_resolution=0.167):
        self.location_resolution = location_resolution
        logging.info(
            f"GribParser initialized with location resolution: {self.location_resolution}"
        )

    def parse_grib_data(self, location, raw_data, data={}):
        if not pygrib:
            return None
        if not raw_data:
            return None
        elif not len(raw_data):
            return None

        f = BytesIO(raw_data)
        raw_messages = []
        while 1:
            # find next occurence of string 'GRIB' (or EOF).
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
            # 5th octet is length of grib message
            lengrib = struct.unpack(">q", f.read(8))[0]
            # read in entire grib message, append to list.
            f.seek(startpos)
            gribmsg = f.read(lengrib)
            raw_messages.append(gribmsg)

        # logger.info(raw_messages[0])
        # convert grib message string to grib message object
        messages = []
        tolerence = self.location_resolution

        first_time_string = pygrib.fromstring(raw_messages[0])

        if not first_time_string:
            return None

        # Parse out the timestamp first
        if data.get("time") is None:
            data["time"] = [first_time_string.validDate]
        else:
            data["time"].append(first_time_string.validDate)

        for m in raw_messages:
            message = pygrib.fromstring(m)

            if not message:
                continue

            var = message.shortName

            if message.has_key("level"):
                if message.level > 1:
                    var += "_" + str(message.level)

            rawvalue, lats, lons = message.data(
                lat1=location.latitude - tolerence,
                lat2=location.latitude + tolerence,
                lon1=location.absolute_longitude - tolerence,
                lon2=location.absolute_longitude + tolerence,
            )
            value = rawvalue.mean().item()

            if data.get(var) is None:
                data[var] = [value]
            else:
                data[var].append(value)

        if not len(messages):
            return None

        return data
