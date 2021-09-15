import logging

from fastapi import APIRouter, HTTPException
from starlette.requests import Request

from service.api import api

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/model", tags=["model"], response_model=api.Output)
def calculate(inp: api.Input, request: Request):
    logger.info("Got request")
    if inp.text == "":
        raise HTTPException(status_code=400, detail="No text")
    if not inp.voice:
        raise HTTPException(status_code=400, detail="No voice")

    res_data = request.app.calculate(inp.text, inp.voice, inp.speed_control_alpha)
    res = api.Output(data=res_data)
    logger.info("Response ready")
    return res


@router.get("/info", tags=["model"], response_model=api.Info)
def get_info(request: Request):
    """Returns models info."""
    res = api.Info(models=request.app.get_info_func(), workers=request.app.workers)
    return res


@router.get("/live", tags=["service"], response_model=api.Live)
def get_live(request: Request):
    """Returns service health state."""
    res = api.Live(ok=request.app.live)
    return res
