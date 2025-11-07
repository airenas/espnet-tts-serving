import base64
import logging

import msgpack
from fastapi import APIRouter, HTTPException
from starlette.requests import Request
from starlette.responses import Response

from service.api import api
from service.espnet.model import CalcResult

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/model", tags=["model"], response_model=api.Output)
def calculate(inp: api.Input, request: Request):
    logger.info("Got request")
    if inp.text == "":
        raise HTTPException(status_code=400, detail="No text")
    if not inp.voice:
        raise HTTPException(status_code=400, detail="No voice")
    if inp.durations_change and len(
            inp.durations_change) > 0 and inp.speed_control_alpha and inp.speed_control_alpha != 1.0:
        raise HTTPException(status_code=400,
                            detail="Either durations_change or speed_control_alpha can be set, not both")

    calc_res: CalcResult = request.app.calculate(text=inp.text,
                                                 voice=inp.voice,
                                                 speed_control_alpha=inp.speed_control_alpha,
                                                 priority=inp.priority,
                                                 durations_change=inp.durations_change,
                                                 pitch_change=inp.pitch_change)

    accept = request.headers.get("accept", "").lower()
    if "application/msgpack" in accept:
        res = api.OutputBin(data=calc_res.features,
                            durations=calc_res.durations,
                            silDuration=calc_res.silence_duration,
                            step=256)
        packed = msgpack.packb(res.dict(), use_bin_type=True)
        return Response(content=packed, media_type="application/msgpack")

    encoded_data = base64.b64encode(calc_res.features)
    res = api.Output(data=encoded_data.decode('ascii'),
                     durations=calc_res.durations,
                     silDuration=calc_res.silence_duration,
                     step=256)
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
