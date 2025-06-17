import math
import requests
import logging


def beach_profile_and_planform(
    beach_lat, beach_lon, fallback_slope, fallback_depth, fallback_orientation
):
    try:
        # Overpass API query to find nearest coastline
        overpass_url = "https://overpass-api.de/api/interpreter"
        query = f"""
        [out:json];
        (
          way(around:500,{beach_lat},{beach_lon})["natural"="coastline"];
        );
        out body;
        >;
        out skel qt;
        """

        response = requests.post(overpass_url, data=query)
        response.raise_for_status()
        osm_data = response.json()

        # Extract nodes and coastline ways
        nodes = {
            elem["id"]: (elem["lat"], elem["lon"])
            for elem in osm_data.get("elements", [])
            if elem["type"] == "node"
        }
        coastline_ways = [
            elem for elem in osm_data.get("elements", []) if elem["type"] == "way"
        ]

        if not coastline_ways:
            raise Exception("No coastline found near this point.")

        nearest_line = [
            [nodes[node_id][1], nodes[node_id][0]]
            for node_id in coastline_ways[0]["nodes"]
            if node_id in nodes
        ]

        # Find the nearest segment
        min_dist = float("inf")
        nearest_segment = None
        for i in range(len(nearest_line) - 1):
            segment = nearest_line[i : i + 2]
            dist = point_line_distance(beach_lat, beach_lon, segment)
            if dist < min_dist:
                min_dist = dist
                nearest_segment = segment

        if nearest_segment is None:
            raise Exception("No shoreline segment found near this point.")

        point1 = nearest_segment[0]
        point2 = interpolate_along_line(nearest_segment, 50)

        lat1, lon1 = point1[1], point1[0]
        lat2, lon2 = point2[1], point2[0]

        # Get elevation
        elev1, elev2 = get_elevations_etopo1([(lat1, lon1), (lat2, lon2)])

        # Calculate slope and orientation
        distance, slope, _ = calculate_slope_and_angle(
            lat1, lon1, lat2, lon2, elev1, elev2
        )
        orientation = (calculate_orientation(lat1, lon1, lat2, lon2) + 90) % 360

        # Adjust slope and depth
        if slope < 0.01:
            slope = fallback_slope
        depth = -elev2 if elev2 < 0 else fallback_depth

        logging.info("Point 1 (onshore): %s, %s, Elevation: %.2f m", lat1, lon1, elev1)
        logging.info("Point 2 (offshore): %s, %s, Elevation: %.2f m", lat2, lon2, elev2)
        logging.info(
            "Distance: %.2f m, Slope: %.4f, Orientation: %.2f°, Depth: %.2f m",
            distance,
            slope,
            orientation,
            depth,
        )

        return depth, slope, orientation

    except Exception as e:
        logging.error("Error determining coastal geometry: %s", e)
        slope = fallback_slope
        depth = fallback_depth
        orientation = fallback_orientation


def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def point_line_distance(lat, lon, line):
    min_dist = float("inf")
    for i in range(len(line) - 1):
        lat1, lon1 = line[i][1], line[i][0]
        lat2, lon2 = line[i + 1][1], line[i + 1][0]
        dist1 = haversine(lat, lon, lat1, lon1)
        dist2 = haversine(lat, lon, lat2, lon2)
        min_dist = min(min_dist, dist1, dist2)
    return min_dist


def interpolate_along_line(line, distance_m):
    total = 0
    for i in range(len(line) - 1):
        lat1, lon1 = line[i][1], line[i][0]
        lat2, lon2 = line[i + 1][1], line[i + 1][0]
        seg = haversine(lat1, lon1, lat2, lon2)
        if total + seg >= distance_m:
            ratio = (distance_m - total) / seg
            lat = lat1 + (lat2 - lat1) * ratio
            lon = lon1 + (lon2 - lon1) * ratio
            return [lon, lat]
        total += seg
    return line[-1]


def get_elevations_etopo1(coords):
    url = "https://api.opentopodata.org/v1/etopo1"
    locations = "|".join([f"{lat},{lon}" for lat, lon in coords])
    params = {"locations": locations}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    results = resp.json()["results"]
    return [r["elevation"] for r in results]


def calculate_slope_and_angle(lat1, lon1, lat2, lon2, elev1, elev2):
    horizontal_distance = haversine(lat1, lon1, lat2, lon2)
    vertical_change = elev2 - elev1
    slope = vertical_change / horizontal_distance
    angle_degrees = math.degrees(math.atan(slope))
    return horizontal_distance, slope, angle_degrees


def calculate_orientation(lat1, lon1, lat2, lon2):
    d_lon = math.radians(lon2 - lon1)
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    x = math.sin(d_lon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(
        d_lon
    )
    bearing = math.atan2(x, y)
    return (math.degrees(bearing) + 360) % 360
