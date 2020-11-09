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
    assert response.json() == {'loaded': False, 'name': 'model.loss.best'}

    app.model_loaded = True
    response = client.get("/info")
    assert response.status_code == 200
    assert response.json() == {'loaded': True, 'name': 'model.loss.best'}


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

    def test_calc(text, model):
        assert text == "in text"
        assert model == "m"
        return "olia"

    app.calculate = test_calc
    response = client.post("/model", json={"text": "in text", "model": "m"})
    assert response.status_code == 200
    assert response.json() == {"data": "olia", "error": None}


def test_environment():
    os.environ["MODEL_NAME"] = "m1"
    os.environ["MODEL_PATH"] = "/m"
    ta = FastAPI()
    service.setup_vars(ta)
    assert ta.model_name == "m1"
    assert ta.model_path == "/m"
