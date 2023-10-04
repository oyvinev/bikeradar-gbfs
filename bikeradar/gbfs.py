import os

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
    is_installed: bool
    is_renting: bool
    is_returning: bool
    last_reported: int = 0


class Feed(BaseModel):
    name: str
    url: str


class SystemInformation(BaseModel):
    system_id: str
    language: str
    name: str


class GBFSApi:
    def __init__(self, base_url: str | None = None):
        if not base_url:
            base_url = os.environ["GBFS_BASE_URL"]

        self.base_url = base_url
        self.feeds = self._get_feeds()
        self.system_information = self._get_system_information()

        try:
            self.station_information_url = next(
                feed.url for feed in self.feeds if feed.name == "station_information"
            )
            self.station_status_url = next(
                feed.url for feed in self.feeds if feed.name == "station_status"
            )
        except StopIteration:
            raise ValueError("Could not find station_information or station_status feed")

    def _get_feeds(self) -> list[Feed]:
        response = requests.get(self.base_url)
        try:
            feeds = list(response.json()["data"].values())[0]["feeds"]
        except KeyError:
            raise ValueError(f"Could not find feeds from '{self.base_url}'")

        return [Feed.model_validate(feed) for feed in feeds]

    def _get_system_information(self) -> SystemInformation:
        system_information_url = next(
            feed.url for feed in self.feeds if feed.name == "system_information"
        )
        response = requests.get(system_information_url)
        return SystemInformation.model_validate(response.json()["data"])

    async def get_stations(self) -> list[Station]:
        response = requests.get(self.station_information_url)
        if response.status_code >= 400:
            raise ValueError("Could not get stations")
        return [Station.model_validate(station) for station in response.json()["data"]["stations"]]

    async def get_status(self) -> dict[str, StationStatus]:
        response = requests.get(self.station_status_url)
        if response.status_code >= 400:
            raise ValueError("Could not get station status")
        return {
            station["station_id"]: StationStatus.model_validate(station)
            for station in response.json()["data"]["stations"]
        }
