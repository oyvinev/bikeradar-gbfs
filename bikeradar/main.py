from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from folium import Map, Marker

from bikeradar.gbfs import Station, StationStatus, get_stations, get_status


def popup(station: Station, station_status: StationStatus) -> str:
    return f"""
    <b>{station.name}</b><br>
    Ledige sykler: {station_status.num_bikes_available}<br>
    Ledige plasser: {station_status.num_docks_available}
    """


def run():
    app = FastAPI()

    @app.get("/", response_class=HTMLResponse)
    async def root():
        m = Map()

        stations = await get_stations()
        station_status = await get_status()

        for station in stations:
            marker = Marker(
                location=[station.lat, station.lon],
                popup=popup(station, station_status[station.station_id]),
            )
            marker.add_to(m)

        return m._repr_html_()

    return app
