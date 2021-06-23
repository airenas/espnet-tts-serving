import os

from fastapi import FastAPI
from fastapi.testclient import TestClient

from service import service


def init_test_app():
    app = FastAPI()
    service.setup_requests(app)
    service.setup_routes(app)
    service.setup_vars(app)
    client = TestClient(app)
    return client, app


def test_read_main():
    client, _ = init_test_app()

    response = client.get("/")
    assert response.status_code == 404


def test_info():
    client, app = init_test_app()

    response = client.get("/info")
    assert response.status_code == 200
    assert response.json() == {'device': 'cpu', 'loaded': False, 'name': '/model/model.zip'}

    app.model_loaded = True
    response = client.get("/info")
    assert response.status_code == 200
    assert response.json() == {'device': 'cpu', 'loaded': True, 'name': '/model/model.zip'}

    app.device = 'cuda'
    response = client.get("/info")
    assert response.status_code == 200
    assert response.json() == {'device': 'cuda', 'loaded': True, 'name': '/model/model.zip'}


def test_calculate_fail():
    client, _ = init_test_app()

    response = client.get("/model")
    assert response.status_code == 405

    response = client.post("/model", json={"olia": "olia"})
    assert response.status_code == 422

    response = client.post("/model", json={"olia": "olia"})
    assert response.status_code == 422


def test_calculate_fail_empty():
    client, _ = init_test_app()

    response = client.post("/model", json={"text": ""})
    assert response.status_code == 400


def test_calculate():
    client, app = init_test_app()

    def test_calc(text, model, speed):
        assert text == "in text"
        assert model == "m"
        assert speed is None
        return "olia"

    app.calculate = test_calc
    response = client.post("/model", json={"text": "in text", "model": "m"})
    assert response.status_code == 200
    assert response.json() == {"data": "olia", "error": None}

def test_calculate_pass_speed():
    client, app = init_test_app()

    def test_calc(text, model, speed):
        assert text == "in text"
        assert model == "m"
        assert speed == 1.2
        return "olia"

    app.calculate = test_calc
    response = client.post("/model", json={"text": "in text", "model": "m", "speedAlpha": 1.2})
    assert response.status_code == 200
    assert response.json() == {"data": "olia", "error": None}

def test_environment():
    os.environ["MODEL_ZIP_PATH"] = "/m1/m.zip"
    os.environ["DEVICE"] = "cuda"
    ta = FastAPI()
    service.setup_vars(ta)
    assert ta.model_zip_path == "/m1/m.zip"
    assert ta.device == "cuda"
