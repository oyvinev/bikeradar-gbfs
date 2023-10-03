from datetime import datetime

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from folium import Icon, Map, Marker

from bikeradar.gbfs import GBFSApi, Station, StationStatus


def popup(station: Station, station_status: StationStatus) -> str:
    return f"""
    <b>{station.name}</b><br>
    Ledige sykler: {station_status.num_bikes_available}<br>
    Ledige plasser: {station_status.num_docks_available}
    """


def icon_color(station_status: StationStatus):
    # TODO: Deal with potential timezone issues
    if datetime.now().timestamp() - station_status.last_reported > 5 * 60:
        return "gray"
    if station_status.num_bikes_available == 0:
        return "red"
    if station_status.num_bikes_available < 3:
        return "orange"
    return "green"


def run():
    gbfs_api = GBFSApi("https://gbfs.urbansharing.com/oslobysykkel.no/gbfs.json", "nb")
    app = FastAPI()

    @app.get("/", response_class=HTMLResponse)
    async def root():
        m = Map()

        stations = await gbfs_api.get_stations()
        station_status = await gbfs_api.get_status()
        m.fit_bounds([(station.lat, station.lon) for station in stations])

        for station in stations:
            marker = Marker(
                location=[station.lat, station.lon],
                popup=popup(station, station_status[station.station_id]),
                icon=Icon(
                    color=icon_color(station_status[station.station_id]),
                    icon="bicycle",
                    prefix="fa",
                ),
            )
            marker.add_to(m)

        return m._repr_html_()

    return app
