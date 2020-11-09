import os

from fastapi import FastAPI
from fastapi.testclient import TestClient

from service import service

app = FastAPI()
service.setup_requests(app)
service.setup_routes(app)
service.setup_vars(app)

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 404


def test_info():
    response = client.get("/info")
    assert response.status_code == 200
    assert response.json() == {'loaded': False, 'name': 'model.loss.best'}


def test_environment():
    os.environ["MODEL_NAME"] = "m1"
    os.environ["MODEL_PATH"] = "/m"
    ta = FastAPI()
    service.setup_vars(ta)
    assert ta.model_name == "m1"
    assert ta.model_path == "/m"
