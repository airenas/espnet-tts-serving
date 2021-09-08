import logging
import os

import requests
import urllib3
from fastapi import FastAPI
from smart_load_balancer.balancer import Balancer
from smart_load_balancer.work import Work, logger

from service.espnet.model import ESPNetModel
from service.metrics import MetricsKeeper

logger = logging.getLogger(__name__)


def setup_prometheus(app):
    from starlette_exporter import PrometheusMiddleware, handle_metrics
    app.add_middleware(PrometheusMiddleware, app_name="espnet-tts-serving", group_paths=True, prefix="model")
    app.metrics = MetricsKeeper()
    app.add_route("/metrics", handle_metrics)


def setup_balancer(app):
    app.balancer = Balancer(wrk_count=2)
    app.balancer.start()


def create_service():
    app = FastAPI(
        title="ESPnet TTS serving",
        version="0.3",
    )
    setup_prometheus(app)
    setup_requests(app)
    setup_routes(app)
    setup_vars(app)
    setup_balancer(app)
    setup_model(app)
    return app


def setup_routes(app):
    """Register routes."""
    from service.routers import model
    app.include_router(model.router, prefix="")


def setup_vars(app):
    app.model_zip_path = os.environ.get("MODEL_ZIP_PATH", "/model/model.zip")
    app.device = os.environ.get("DEVICE", "cpu")
    app.model_loaded = False


def setup_model(app):
    def calc_model(voice, text, workers_data):
        w_name = workers_data.get("name")
        model = workers_data.get("model")
        if w_name != voice:
            if w_name:
                logger.info("Unloading model for %s", w_name)
            workers_data["name"] = ""
            workers_data["model"] = None
            logger.info("Loading model for %s ", voice)
            with app.metrics.load_metric.time():
                model = ESPNetModel(app.model_zip_path, app.device)
            workers_data["model"] = model
            workers_data["name"] = voice

        with app.metrics.calc_metric.time():
            return model.calculate(text)

    def calc(text, voice):
        if not voice:
            raise Exception("no voice")
        work = Work(name=voice, data=text, work_func=calc_model)
        app.balancer.add_wrk(work)
        res = work.wait()
        if res.err is not None:
            raise res.err
        return res.res

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
