import surfpy
from cache import Cache
from NOAA_data_retrieval import retrieve_new_data
import json
import datetime
import base64
from io import BytesIO
from models import SurfReportResponse


def get_wave_forecast(
    wave_model: str,
    cache: Cache,
    selected_location: surfpy.Location,
    lat=str,
    lon=str,
    hours_to_forecast=24,
) -> object:
    location = surfpy.Location(lat, lon, altitude=0, name=selected_location)
    location.depth = 10.0
    location.angle = 200.0
    location.slope = 0.28

    key = f"{location.name}"
    cache_item = cache.get_item(key)

    if cache_item is not None:
        # TODO: cache hit and miss paths should return an identical result
        # a caller should not observe a difference in behaviour (apart from latency) between cached vs fresh result
        cache_item['chart'] = json.loads(cache_item['chart'])
        response = SurfReportResponse(**cache_item)

        return response


    # call retrieve_new_data for new forecast
    forecast_data = retrieve_new_data(wave_model, hours_to_forecast, location)

    buoyStations = surfpy.BuoyStations()
    buoyStations.fetch_stations()
    test_location = surfpy.Location(36.7783, -119.4179)

    def find_closest_buoy(s, location, active=False):
        if len(s.stations) < 1:
            return None

        closest_buoy = None
        closest_distance = float('inf')

        for station in s.stations:
            if active and not station.active:
                continue

            dist = location.distance(station.location)
            if dist < closest_distance:
                closest_buoy = station
                closest_distance = dist

        return closest_buoy

    result = find_closest_buoy(buoyStations, test_location)

    img = BytesIO()
    forecast_data['chart'].savefig(img, format="png")
    plot_base64_image = base64.b64encode(img.getvalue()).decode("utf8")

    expires_at = datetime.datetime.now().day + 1
    serialized_object = json.dumps(plot_base64_image)
    wave_height = forecast_data['current_wave_height']

    # set_item in cache
    cache.set_item(key, serialized_object, wave_height, expires_at)

    response = SurfReportResponse(**{
        'chart': plot_base64_image,
        'wave_height': forecast_data['current_wave_height']
    })

    return response
