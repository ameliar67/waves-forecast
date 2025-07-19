import json
import logging
from typing import Awaitable, Callable, Hashable, Self, TypeVar, TypedDict

import aiohttp
import surfpy


class KnownLocation(TypedDict):
    name: str
    state: str
    beach_latitude: float
    beach_longitude: float
    jetty_obstructions: list[int]
    closest_station: surfpy.BuoyStation | None
    closest_distance: int | None


client_logger = logging.getLogger("aiohttp.client")


async def on_request_end(_1, _2, params: aiohttp.TraceRequestEndParams):
    client_logger.debug(
        "Request end %s %s [%d]",
        params.method,
        params.url,
        params.response.status,
    )


trace_config = aiohttp.TraceConfig()
trace_config.on_request_end.append(on_request_end)


TArg = TypeVar("TArg", bound=Hashable)
TResult = TypeVar("TResult")


class ForecastContext:
    def __init__(self):
        self.cache = {}
        self.buoy_stations = surfpy.BuoyStations()
        self.tide_stations = surfpy.TideStations()
        self.known_surf_locations: dict[str, list[KnownLocation]] = {}

    async def __aenter__(self):
        self.http_session = aiohttp.ClientSession(trace_configs=[trace_config])
        self.http_session.headers["User-Agent"] = "waves-forecast/1.0.0"

        # open pre-estabilished list of known surfing locations
        with open("known_locations.json") as fp:
            self.known_surf_locations = json.load(fp)

        # fetch NOAA station data for wave heights and tides (data comes from seperate stations)
        self.buoy_stations.fetch_stations()
        self.tide_stations.fetch_stations()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.http_session.__aexit__(exc_type, exc_val, exc_tb)

    async def get_cached_or_compute(
        self,
        key: TArg,
        generate_func: Callable[[Self, TArg], Awaitable[TResult]],
    ) -> TResult:
        if key not in self.cache:
            self.cache[key] = await generate_func(self, key)

        return self.cache[key]
