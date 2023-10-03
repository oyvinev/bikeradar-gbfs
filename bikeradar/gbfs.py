import requests
from pydantic import BaseModel


class Station(BaseModel):
    station_id: str
    name: str
    address: str
    lat: float
    lon: float
    capacity: int


async def get_stations() -> list[Station]:
    response = requests.get(
        "https://gbfs.urbansharing.com/oslobysykkel.no/station_information.json"
    )
    return [Station.model_validate(station) for station in response.json()["data"]["stations"]]
