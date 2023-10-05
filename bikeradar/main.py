from datetime import datetime
from pathlib import Path
from typing import Literal

import jinja2
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from folium import Icon, Map, Marker

from bikeradar.gbfs import GBFSApi, Station, StationStatus


def popup(station: Station, station_status: StationStatus | None) -> str:
    """Return HTML for popup when clicking on a station marker"""
    if not station_status:
        return f"""
        <b>{station.name}</b><br>
        Ingen data
        """

    return f"""
    <b>{station.name}</b><br>
    <span style="white-space: nowrap;">Ledige sykler: {station_status.num_bikes_available}</span><br>
    <span style="white-space: nowrap;">Ledige plasser: {station_status.num_docks_available}</span><br>
    """


def icon_color(station_status: StationStatus | None):
    """Return color for station marker, based on number of bikes available"""
    if not station_status:
        return "gray"
    # TODO: Deal with potential timezone issues
    if datetime.now().timestamp() - station_status.last_reported > 5 * 60:
        return "gray"
    if station_status.num_docks_available == 0:
        return "blue"
    if station_status.num_bikes_available == 0:
        return "red"
    if station_status.num_bikes_available < 3:
        return "orange"
    return "green"


def run():
    """
    Entrypoint for running the app

    Creates the API for accessing GBFS data, and creates the FastAPI app
    """
    gbfs_api = GBFSApi()
    app = FastAPI()

    # TODO: Add more fine-grained exception handling
    @app.exception_handler(Exception)
    async def exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"message": f"Unable to present data from GBFS API ({gbfs_api.base_url})"},
        )

    @app.get("/", response_class=HTMLResponse)
    async def index():
        """
        Return the template HTML.

        No map or markers added yet - this is handled by htmx request to _update
        """
        m = Map()
        with Path(__file__).parent / "template.html" as f:
            template = jinja2.Template(f.read_text())
        m.get_root().render()
        header = m.get_root().header.render()  # type: ignore
        return template.render(
            title=gbfs_api.system_information.name,
            header=header,
            legend={
                "blue": "Fullt",
                "green": "Ledige sykler",
                "orange": "Få ledige sykler",
                "red": "Ingen ledige sykler",
                "gray": "Ingen info",
            },
        )

    @app.get("/_render", response_class=HTMLResponse)
    async def render(
        lat: float | Literal["auto"] = "auto",
        lng: float | Literal["auto"] = "auto",
        zoom: int | Literal["auto"] = "auto",
    ):
        """
        Return HTML for the map, with markers added

        If lat, lng or zoom is set to "auto", the map will be centered and zoomed to fit all stations.
        Otherwise, the map will be centered at the given lat/lng, and zoomed to the given zoom level.
        """

        # Fetch data from GBFS API
        stations = await gbfs_api.get_stations()
        station_status = await gbfs_api.get_status()

        # Create and position map
        if any(param == "auto" for param in [lat, lng, zoom]):
            m = Map()
            m.fit_bounds([(station.lat, station.lon) for station in stations])
        else:
            m = Map(location=[lat, lng], zoom_start=zoom)  # type: ignore

        # Add station markers
        for station in stations:
            marker = Marker(
                location=[station.lat, station.lon],
                popup=popup(station, station_status.get(station.station_id)),
                icon=Icon(
                    color=icon_color(station_status.get(station.station_id)),
                    icon="bicycle",
                    prefix="fa",
                ),
            )
            marker.add_to(m)

        # Create and return HTML for map
        m.get_root().render()
        body_html = m.get_root().html.render()  # type: ignore
        script = m.get_root().script.render()  # type: ignore

        template = jinja2.Template("{{ map_html|safe }}<script>{{ map_js|safe }}</script>")
        return template.render(map_html=body_html, map_js=script)

    return app
