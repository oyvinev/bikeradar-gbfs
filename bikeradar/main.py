from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from folium import Map


def run():
    app = FastAPI()

    @app.get("/", response_class=HTMLResponse)
    async def root():
        m = Map()
        return m._repr_html_()

    return app
