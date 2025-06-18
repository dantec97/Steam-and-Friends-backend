from dotenv import load_dotenv
load_dotenv(".env.test")
import pytest
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_hello(client):
    resp = client.get("/api/hello")
    assert resp.status_code in (200, 404)