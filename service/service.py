import os

import requests
import urllib3
from fastapi import FastAPI
from fastapi.logger import logger

from service.espnet.model import EspNETModel


def create_service():
    app = FastAPI(
        title="EspNET TTS serving",
        version="0.1",
    )
    setup_requests(app)
    setup_routes(app)
    setup_vars(app)
    setup_model(app)
    return app


def setup_routes(app):
    """Register routes."""
    from service.routers import model
    app.include_router(model.router, prefix="")


def setup_vars(app):
    logger.info("Loading model")
    app.model_name = os.environ.get("MODEL_NAME", "model.loss.best")
    app.model_path = os.environ.get("MODEL_PATH", "/model")
    app.model_loaded = False


def setup_model(app):
    esp_model = EspNETModel(app.model_path, app.model_name)

    def calc(text, model):
        return esp_model.calculate(text)

    app.calculate = calc
    app.model_loaded = True
    logger.info("Loaded")


def setup_requests(app):
    """Set up a session for making HTTP requests."""
    session = requests.Session()
    session.headers["Content-Type"] = "application/json"
    retry = urllib3.util.Retry(total=5, status=2, backoff_factor=0.3)
    retry_adapter = requests.adapters.HTTPAdapter(max_retries=retry)

    session.mount("http://", retry_adapter)

    app.requests = session
