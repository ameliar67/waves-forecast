import folium
from folium.plugins import MarkerCluster


def generate_map(stations):
    map = folium.Map(location=[1, 1], zoom_start=2.5)
    marker_cluster = MarkerCluster().add_to(map)

    for loc_id, buoyStation in stations.items():
        folium.Marker(
            location=[buoyStation["latitude"], buoyStation["longitude"]],
            popup=folium.Popup(
                f"<div><a href='/forecast/{loc_id}'>{buoyStation['name']}</a></div>\n",
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
