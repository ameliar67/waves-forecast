import surfpy
from metocean_data_retrieval import WaveForecastData, retrieve_new_data
from beach_morphology import beach_profile_and_planform
from context import ForecastContext


async def get_wave_forecast(
    context: ForecastContext,
    beach_name: str,
    wave_model: surfpy.WaveModel,
    buoy_lat: float,
    buoy_lon: float,
    tide_stations: list[str] | None,
    beach_lat: float,
    beach_lon: float,
    jetty_obstructions: list[int],
    hours_to_forecast=384,
) -> WaveForecastData:

    # Fallback default values
    fallback_depth = 10.0
    fallback_slope = 0.02
    fallback_orientation = 180.0  # facing south

    # use longitude to ensure semi accurate fallback orientation
    if beach_lon > -81 and beach_lon < -66:
        # beach is located on US East Coast - faces East
        fallback_orientation = 90.0
    elif beach_lon > -126 and beach_lon < -117:
        # beach is located on US West Coast - faces West
        fallback_orientation = 270.0

    # calculate beach characteristics for accurate forecast
    depth, slope, orientation = beach_profile_and_planform(
        beach_lat, beach_lon, fallback_slope, fallback_depth, fallback_orientation
    )

    # Setup location
    location = surfpy.Location(
        latitude=buoy_lat,
        longitude=buoy_lon,
        name=beach_name,
        altitude=0,
        depth=depth,
        angle=orientation,
        slope=slope,
    )

    # Retrieve forecast data
    data = await retrieve_new_data(
        context,
        wave_model,
        hours_to_forecast,
        location,
        tide_stations,
        jetty_obstructions,
    )

    return data
