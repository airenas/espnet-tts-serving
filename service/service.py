import logging
import os

import requests
import urllib3
from fastapi import FastAPI, HTTPException
from smart_load_balancer.balancer import Balancer
from smart_load_balancer.strategy.strategy import GroupsByNameWithTimeNoSameWorker
from smart_load_balancer.work import Work

from service.config import Config
from service.espnet.model import ESPNetModel
from service.metrics import MetricsKeeper, ElapsedLogger
from service.utils import len_fix

logger = logging.getLogger(__name__)


def setup_prometheus(app):
    from starlette_exporter import PrometheusMiddleware, handle_metrics
    app.add_middleware(PrometheusMiddleware, app_name="espnet-tts-serving", group_paths=True, prefix="model")
    app.metrics = MetricsKeeper()
    app.add_route("/metrics", handle_metrics)


def setup_balancer(app):
    app.balancer = Balancer(wrk_count=app.workers, strategy=GroupsByNameWithTimeNoSameWorker())
    app.balancer.start()


def setup_config(app):
    with open(app.config_file, 'r') as data:
        app.voices = Config(data, app.device)
    app.get_info_func = app.voices.get_info


def test_models(app):
    for key in app.voices.voices:
        vc = app.voices.voices.get(key)
        logger.info("Test model load for %s ", vc.name)
        with ElapsedLogger(logger.info, "load time"):
            ESPNetModel(vc.data, vc.device, vc.speed_shift)
        logger.info("OK - model can be loaded for %s ", vc.name)


def create_service():
    app = FastAPI(
        title="ESPnet TTS serving",
        version="0.4",
    )
    setup_vars(app)
    setup_config(app)
    test_models(app)
    setup_prometheus(app)
    setup_requests(app)
    setup_routes(app)
    setup_balancer(app)
    setup_model(app)
    app.live = True
    return app


def setup_routes(app):
    """Register routes."""
    from service.routers import model
    app.include_router(model.router, prefix="")


def setup_vars(app):
    app.config_file = os.environ.get("CONFIG_FILE", "/model/config.yaml")
    app.device = os.environ.get("DEVICE", "cpu")
    app.workers = int(os.environ.get("WORKERS", "1"))
    if app.workers == 0:
        raise Exception("No workers configured env.WORKERS")
    app.live = False


class ModelData:
    def __init__(self, text, speed_control_alpha):
        self.speed_control_alpha = speed_control_alpha
        self.text = text


def setup_model(app):
    def calc_model(voice: str, in_data: ModelData, workers_data):
        w_name = workers_data.get("name")
        model = workers_data.get("model")
        if w_name != voice:
            if w_name:
                logger.info("Unloading model for %s", w_name)
            workers_data["name"] = ""
            workers_data["model"] = None
            logger.info("Loading model for %s ", voice)
            vc = app.voices.get(voice)
            if vc is None:
                raise HTTPException(status_code=400, detail="No voice '%s'" % voice)
            with app.metrics.load_metric.labels(voice).time():
                with ElapsedLogger(logger.info, "load time"):
                    model = ESPNetModel(vc.data, vc.device, vc.speed_shift)
            workers_data["model"] = model
            workers_data["name"] = voice
            workers_data["silence_duration"] = vc.silence_duration

        with app.metrics.calc_metric.labels(voice).time():
            res = model.calculate(in_data.text, in_data.speed_control_alpha)
        res["silence_duration"] = len_fix(workers_data["silence_duration"], in_data.speed_control_alpha)
        return res

    def calc(text, voice, speed_control_alpha, priority: int = 0):
        with ElapsedLogger(logger.info, "calculate"):
            if not voice:
                raise Exception("no voice")
            work = Work(name=voice, data=ModelData(text, speed_control_alpha), work_func=calc_model, priority=priority)
            app.balancer.add_wrk(work)
            res = work.wait()
            if res.err is not None:
                raise res.err
            return res.res

    app.calculate = calc
    logger.info("Ready")


def setup_requests(app):
    """Set up a session for making HTTP requests."""
    session = requests.Session()
    session.headers["Content-Type"] = "application/json"
    retry = urllib3.util.Retry(total=5, status=2, backoff_factor=0.3)
    retry_adapter = requests.adapters.HTTPAdapter(max_retries=retry)

    session.mount("http://", retry_adapter)

    app.requests = session
