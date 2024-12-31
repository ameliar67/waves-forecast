import surfpy
import folium
import filteredLocations
from folium.plugins import MarkerCluster

def generate_map():

    map = folium.Map(location=[1, 1], zoom_start=2.5)
    marker_cluster = MarkerCluster().add_to(map)

    stations = filteredLocations.filterLocations(surfpy.BuoyStations())

    for buoyStation in stations.keys():

        folium.Marker(
            location=[stations[buoyStation]["latitude"], stations[buoyStation]["longitude"]],
            popup=folium.Popup(
                f"""<div id={buoyStation} onclick="goToForecastPage('{buoyStation}')">{buoyStation}</div>
        """,
                max_width=200,
            ),
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

    map.get_root().html.add_child(folium.Element(css))

    map_string = map.get_root().render()

    return map_string
