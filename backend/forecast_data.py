import surfpy
from data_retrieval import WaveForecastData, retrieve_new_data


async def get_wave_forecast(
    wave_model: surfpy.WaveModel,
    lat=str,
    lon=str,
    hours_to_forecast=384,
) -> WaveForecastData:

    location = surfpy.Location(lat, lon, altitude=0)
    location.depth, location.angle, location.slope = 10.0, 200.0, 0.28

    data = await retrieve_new_data(wave_model, hours_to_forecast, location)

    return data
