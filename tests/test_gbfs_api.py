import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).parent.parent))

from bikeradar.gbfs import GBFSApi


def test_get_feeds():
    gbfs_api = GBFSApi("http://localhost:9000/gbfs.json", "nb")
    assert len(gbfs_api.feeds) == 3
    assert {"station_information", "station_status", "system_information"} == {
        feed.name for feed in gbfs_api.feeds
    }

    with pytest.raises(ValueError, match="Could not find feeds for language 'en'"):
        GBFSApi("http://localhost:9000/gbfs.json", "en")


@pytest.mark.asyncio
async def test_get_stations():
    gbfs_api = GBFSApi("http://localhost:9000/gbfs.json", "nb")
    gbfs_api.station_information_url = "http://localhost:9000/does_not_exist.json"
    with pytest.raises(ValueError, match="Could not get stations"):
        await gbfs_api.get_stations()


@pytest.mark.asyncio
async def test_get_status():
    gbfs_api = GBFSApi("http://localhost:9000/gbfs.json", "nb")
    gbfs_api.station_status_url = "http://localhost:9000/does_not_exist.json"
    with pytest.raises(ValueError, match="Could not get station status"):
        await gbfs_api.get_status()
