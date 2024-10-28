import surfpy
import pickle
import surf_data


def retrieveNewData(wave_model, hours_to_forecast, wave_location, wind_location):

    wave_grib_data = wave_model.fetch_grib_datas(0, hours_to_forecast)
    raw_wave_data = wave_model.parse_grib_datas(wave_location, wave_grib_data)

    if not raw_wave_data:
        return None

    buoy_data = wave_model.to_buoy_data(raw_wave_data)
    weather_data = surfpy.WeatherApi.fetch_hourly_forecast(wind_location)
    wave_data = surfpy.merge_wave_weather_data(buoy_data, weather_data)

    for d in wave_data:
        d.solve_breaking_wave_heights(wave_location)

    serialised_array = pickle.dumps(wave_data)

    connection = surf_data.get_db_connection()
    with open("schema.sql") as f:
        connection.executescript(f.read())

    cur = connection.cursor()
    cur.execute(
        "INSERT INTO waveData (title, content, location) VALUES (?, ?, ?)",
        ("Data", serialised_array, wave_location.name),
    )
    connection.commit()
    connection.close()

    return wave_data
