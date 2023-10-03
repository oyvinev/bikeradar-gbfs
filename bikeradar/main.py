from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from folium import Map, Marker

from bikeradar.gbfs import get_stations


def run():
    app = FastAPI()

    @app.get("/", response_class=HTMLResponse)
    async def root():
        m = Map()

        stations = await get_stations()

        for station in stations:
            marker = Marker(location=[station.lat, station.lon], popup=station.name)
            marker.add_to(m)

        return m._repr_html_()

    return app
