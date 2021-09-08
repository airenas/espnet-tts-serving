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

    res_data = request.app.calculate(inp.text, inp.voice)
    res = api.Output(data=res_data)
    logger.info("Response ready")
    return res


@router.get("/info", tags=["model"], response_model=api.Info)
def get_info(request: Request):
    """Returns models info."""
    res = api.Info(name=request.app.model_zip_path, device=request.app.device, loaded=request.app.model_loaded)
    return res
