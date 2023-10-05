import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).parent.parent))

from bikeradar.gbfs import GBFSApi


def test_initialize_gbfs_api():
    """Test that we can initialize a GBFSApi object, and fetch feeds and system information"""
    gbfs_api = GBFSApi("http://localhost:9000/gbfs.json")
    assert gbfs_api.system_information.system_id == "oslobysykkel"
    assert gbfs_api.system_information.language == "nb"
    assert gbfs_api.system_information.name == "Oslo Bysykkel"

    assert len(gbfs_api.feeds) == 3
    assert {"station_information", "station_status", "system_information"} == {
        feed.name for feed in gbfs_api.feeds
    }


def test_erronous_gbfs_api():
    """Test that we get a meaningful error message if the base_url is not found"""
    url = "http://localhost:9000/does_not_exist.json"
    with pytest.raises(ValueError, match=f"Could not get feeds from '{url}'"):
        GBFSApi("http://localhost:9000/does_not_exist.json")


@pytest.mark.asyncio
async def test_get_stations():
    """Test that we can get stations from the station_information feed"""
    gbfs_api = GBFSApi("http://localhost:9000/gbfs.json")
    stations = await gbfs_api.get_stations()
    assert len(stations) == 3

    # Test that we get a meaningful error message if the station_information feed is not found
    gbfs_api.station_information_url = "http://localhost:9000/does_not_exist.json"
    with pytest.raises(ValueError, match="Could not get stations"):
        await gbfs_api.get_stations()


@pytest.mark.asyncio
async def test_get_status():
    """Test that we can get station status from the station_status feed"""
    gbfs_api = GBFSApi("http://localhost:9000/gbfs.json")

    station_status = await gbfs_api.get_status()
    assert len(station_status) == 3

    # Test that we get a meaningful error message if the station_status feed is not found
    gbfs_api.station_status_url = "http://localhost:9000/does_not_exist.json"
    with pytest.raises(ValueError, match="Could not get station status"):
        await gbfs_api.get_status()
