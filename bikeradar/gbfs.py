import requests
from pydantic import BaseModel


class Station(BaseModel):
    station_id: str
    name: str
    address: str
    lat: float
    lon: float
    capacity: int


class StationStatus(BaseModel):
    station_id: str
    num_bikes_available: int
    num_docks_available: int
    is_installed: int
    is_renting: int
    is_returning: int
    last_reported: int


async def get_stations() -> list[Station]:
    response = requests.get(
        "https://gbfs.urbansharing.com/oslobysykkel.no/station_information.json"
    )
    return [Station.model_validate(station) for station in response.json()["data"]["stations"]]


async def get_status() -> dict[str, StationStatus]:
    response = requests.get("https://gbfs.urbansharing.com/oslobysykkel.no/station_status.json")
    return {
        station["station_id"]: StationStatus.model_validate(station)
        for station in response.json()["data"]["stations"]
    }
