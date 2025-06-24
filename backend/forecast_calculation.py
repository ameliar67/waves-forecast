import surfpy
from metocean_data_retrieval import WaveForecastData, retrieve_new_data
from beach_morphology import beach_profile_and_planform


async def get_wave_forecast(
    wave_model: surfpy.WaveModel,
    buoy_lat=str,
    buoy_lon=str,
    tide_stations=list,
    hours_to_forecast=384,
    beach_lat=float,
    beach_lon=float,
    jetty_obstructions=list
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
    location = surfpy.Location(buoy_lat, buoy_lon, altitude=0)
    location.depth = depth
    location.slope = slope
    location.angle = orientation

    # Retrieve forecast data
    data = await retrieve_new_data(
        wave_model, hours_to_forecast, location, tide_stations, jetty_obstructions
    )

    return data
