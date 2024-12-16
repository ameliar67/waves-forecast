import surf_data
import surfpy
import xml.etree.ElementTree as ET
from cache import Cache
import os
from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.requests import Request
from starlette.routing import Route

path = os.path.dirname(os.path.abspath(__file__))
db = os.path.join(path, 'database.db')

cache = Cache(db)
cache.migrate()

locations_dict = {}

tree = ET.parse(os.path.join(path, "../libs/surfpy/surfpy/tests/data/activestations.xml"))
root = tree.getroot()
for child in root:
    locations_dict[child.attrib["name"]] = {
        "id": child.attrib["id"],
        "longitude": float(child.attrib["lon"]),
        "latitude": float(child.attrib["lat"]),
    }


def generate_wave_forecast(selected_location):

    wave_forecast = surf_data.get_wave_forecast(
        wave_model=surfpy.wavemodel.us_west_coast_gfs_wave_model(),
        cache=cache,
        selectedLocation=selected_location,
        lat=locations_dict[selected_location]["latitude"],
        lon=locations_dict[selected_location]["longitude"],
    )

    if not wave_forecast:
        raise ValueError("Failed to get forecast from NOAA")

    return wave_forecast

async def landing_page(request):
    with open("templates/index.html", "r") as file:
        html_content = file.read()

    locations = locations_dict.keys()

    dropdown_placeholder = "<select name=\"location\" id=\"location\">"
    options = "".join([f'<option value="{location}">{location}</option>' for location in locations])

    html_content = html_content.replace("<select name=\"location\" id=\"location\">", dropdown_placeholder + options)

    return HTMLResponse(html_content)


async def forecast(request: Request):
    form_data = await request.form()

    selected_location = form_data.get('location')
    plot_image = generate_wave_forecast(selected_location)

    with open("templates/forecast.html", "r") as file:
        html_content = file.read()

    try:

        locations = locations_dict.keys()

        dropdown_placeholder = "<select name=\"location\" id=\"location\">"
        options = "".join([f'<option value="{location}">{location}</option>' for location in locations])

        html_content = html_content.replace("<select name=\"location\" id=\"location\">", dropdown_placeholder + options)
        html_content = html_content.replace("{{ plot_url }}", plot_image)
        html_content = html_content.replace("{{ location }}", selected_location)

        return HTMLResponse(html_content)

    except Exception as e:
        error_html = f'''
        <html>
        <body>
            <h1>Error generating surf report: {e}</h1>
            <a href="/">Back to form</a>
        </body>
        </html>
        '''
        return HTMLResponse(content=error_html, status_code=500)
    

routes = [
    Route('/', landing_page),
    Route('/forecast.html', forecast, methods=["POST"]),  
]

app = Starlette(debug=True, routes=routes)
