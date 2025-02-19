import logging

import surfpy

all_wave_models = [
    surfpy.wavemodel.atlantic_gfs_wave_model(),
    surfpy.wavemodel.us_west_coast_gfs_wave_model(),
    surfpy.wavemodel.southern_gfs_wave_model(),
    surfpy.wavemodel.eastpacific_gfs_wave_model(),
    surfpy.wavemodel.arctic_gfs_wave_model(),
    surfpy.wavemodel.alaska_gfs_wave_model(),
]

fallback_model = surfpy.wavemodel.global_gfs_wave_model_25km()


def get_wave_model(lat: int, lon: int):
    loc = surfpy.Location(lat, lon)
    for m in all_wave_models:
        if m.contains_location(loc):
            logging.info(
                "Using model %s for location %f,%f", m.description, lat, lon
            )
            return m

    logging.info(
        "Using fallback model %s for location %f,%f",
        fallback_model.description,
        lat,
        lon,
    )
    return fallback_model
