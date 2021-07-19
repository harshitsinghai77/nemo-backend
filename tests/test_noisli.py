from fastapi.testclient import TestClient

from noiist import __version__
from main import app

client = TestClient(app)


def test_version():
    assert __version__ == "0.1.0"


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.text == "App succesfully running."
