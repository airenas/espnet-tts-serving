import os
from typing import List

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from service import service
from service.api import api


def get_info_test() -> List[api.ModelInfo]:
    return [api.ModelInfo(name="olia", device="cpu")]


def init_test_app():
    app = FastAPI()
    service.setup_requests(app)
    service.setup_routes(app)
    service.setup_vars(app)
    app.get_info_func = get_info_test
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
    assert response.json() == {'models': [{'device': 'cpu', 'name': 'olia'}], 'workers': 1}

    app.workers = 2
    response = client.get("/info")
    assert response.status_code == 200
    assert response.json() == {'models': [{'device': 'cpu', 'name': 'olia'}], 'workers': 2}

    def empty():
        return []

    app.get_info_func = empty
    response = client.get("/info")
    assert response.status_code == 200
    assert response.json() == {'models': [], 'workers': 2}


def test_live():
    client, app = init_test_app()

    app.live = True
    response = client.get("/live")
    assert response.status_code == 200
    assert response.json() == {'ok': True}

    app.live = False
    response = client.get("/live")
    assert response.status_code == 200
    assert response.json() == {'ok': False}


def test_calculate_fail():
    client, _ = init_test_app()

    response = client.get("/model")
    assert response.status_code == 405

    response = client.post("/model", json={"olia": "olia", "voice": "a"})
    assert response.status_code == 422

    response = client.post("/model", json={"olia": "olia", "voice": "a"})
    assert response.status_code == 422


def test_calculate_fail_empty():
    client, _ = init_test_app()

    response = client.post("/model", json={"text": ""})
    assert response.status_code == 400


def test_calculate():
    client, app = init_test_app()

    def test_calc(text, model, speedAlpha, priority):
        assert text == "in text"
        assert model == "m"
        assert speedAlpha is None
        assert priority == 0
        return "olia"

    app.calculate = test_calc
    response = client.post("/model", json={"text": "in text", "voice": "m"})
    assert response.status_code == 200
    assert response.json() == {"data": "olia", "error": None}


def test_calculate_pass_speed():
    client, app = init_test_app()

    def test_calc(text, model, speedAlpha, priority):
        assert text == "in text"
        assert model == "m"
        assert speedAlpha == 1.2
        return "olia"

    app.calculate = test_calc
    response = client.post("/model", json={"text": "in text", "voice": "m", "speedAlpha": 1.2})
    assert response.status_code == 200
    assert response.json() == {"data": "olia", "error": None}


def test_calculate_pass_priority():
    client, app = init_test_app()

    def test_calc(text, model, speedAlpha, priority):
        assert text == "in text"
        assert model == "m"
        assert priority == 1000
        return "olia"

    app.calculate = test_calc
    response = client.post("/model", json={"text": "in text", "voice": "m", "speedAlpha": 1.2, "priority": 1000})
    assert response.status_code == 200
    assert response.json() == {"data": "olia", "error": None}


def test_environment():
    os.environ["CONFIG_FILE"] = "/m1/c.yaml"
    os.environ["DEVICE"] = "cuda"
    os.environ["WORKERS"] = "12"
    ta = FastAPI()
    service.setup_vars(ta)
    assert ta.config_file == "/m1/c.yaml"
    assert ta.device == "cuda"
    assert ta.workers == 12


def test_env_fail():
    os.environ["WORKERS"] = "0"
    ta = FastAPI()
    with pytest.raises(Exception):
        service.setup_vars(ta)
