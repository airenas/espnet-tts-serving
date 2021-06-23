from fastapi import APIRouter, HTTPException
from starlette.requests import Request

from service.api import api

router = APIRouter()


@router.post("/model", tags=["model"], response_model=api.Output)
async def calculate(input: api.Input, request: Request):
    if input.text == "":
        raise HTTPException(status_code=400, detail="No text")

    res_data = request.app.calculate(input.text, input.model, input.speed_control_alpha)
    res = api.Output(data=res_data)
    return res


@router.get("/info", tags=["model"], response_model=api.Info)
async def get_info(request: Request):
    """Returns models info."""
    res = api.Info(name=request.app.model_zip_path, device=request.app.device, loaded=request.app.model_loaded)
    return res
