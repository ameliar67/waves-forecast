import surfpy
import folium
from folium.plugins import MarkerCluster

def generate_map() :

    m = folium.Map(location=[1,1], zoom_start=2.5)
    marker_cluster = MarkerCluster().add_to(m)

    buoyStations = surfpy.BuoyStations()
    buoyStations.fetch_stations()
    
    for buoyStation in buoyStations.stations:

        if(buoyStation.buoy_type == "tao" or buoyStation.buoy_type == "oilrig" or buoyStation.buoy_type == "dart"):
            continue
        folium.Marker(
            location=[buoyStation.location.latitude, buoyStation.location.longitude],
            popup=folium.Popup(f"""<div id={buoyStation.location.name} onclick="goToForecastPage('{buoyStation.location.name}')">{buoyStation.location.name}</div>
        """,
        max_width=200
    )
        ).add_to(marker_cluster)

    css = """
    <style>
    #map {
        position: absolute !important;
        top: 35% !important;
        height: 70% !important;
    }
    .leaflet-popup-content-wrapper:hover  {
        text-decoration: underline;
        cursor: pointer;
    }
    </style>
    """

    m.get_root().html.add_child(folium.Element(css))


    map_string = m.get_root().render()

    return map_string
