import subprocess
import time
from contextlib import contextmanager
from http.server import HTTPServer, SimpleHTTPRequestHandler

import pytest
import requests


@contextmanager
@pytest.fixture(scope="session", autouse=True)
def local_gbfs_server():
    """Serve the testdata directory on localhost:9000. Ensure that the server is closed after the test."""
    p = subprocess.Popen(["python", "-m", "http.server", "9000"], cwd="tests/testdata")

    # Wait for the server to start
    MAX_WAIT = 10
    start_wait = time.time()
    while True:
        try:
            requests.get("http://localhost:9000/")
            break
        except:
            assert p.poll() is None
            time.sleep(0.1)
            if time.time() - start_wait > MAX_WAIT:
                raise TimeoutError("Could not start local test server")
            continue
    try:
        yield
    finally:
        p.terminate()
