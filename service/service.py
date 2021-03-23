import os

import requests
import urllib3
from fastapi import FastAPI
from fastapi.logger import logger

from service.espnet.model import ESPNetModel


def setup_prometheus(app):
    from starlette_exporter import PrometheusMiddleware, handle_metrics
    app.add_middleware(PrometheusMiddleware, app_name="espnet-tts-serving", group_paths=True,)
    app.add_route("/metrics", handle_metrics)


def create_service():
    app = FastAPI(
        title="ESPnet TTS serving",
        version="0.2",
    )
    setup_prometheus(app)
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
    app.model_zip_path = os.environ.get("MODEL_ZIP_PATH", "/model/model.zip")
    app.device = os.environ.get("DEVICE", "cpu")
    app.model_loaded = False


def setup_model(app):
    esp_model = ESPNetModel(app.model_zip_path, app.device)

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
