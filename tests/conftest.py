import subprocess
from contextlib import contextmanager
from http.server import HTTPServer, SimpleHTTPRequestHandler

import pytest


@contextmanager
@pytest.fixture(scope="session", autouse=True)
def local_gbfs_server():
    """Serve the testdata directory on localhost:9000. Ensure that the server is closed after the test."""
    p = subprocess.Popen(["python", "-m", "http.server", "9000"], cwd="tests/testdata")
    try:
        yield
    finally:
        p.terminate()
