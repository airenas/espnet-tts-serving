from fastapi import APIRouter
from starlette.requests import Request

from service.api import api

router = APIRouter()


@router.post("/model", tags=["model"], response_model=api.Output)
async def calculate(input: api.Input, request: Request):
    res_data = request.app.calculate(input.text, input.model)
    res = api.Output(data=res_data)
    return res


@router.get("/info", tags=["model"], response_model=api.Info)
async def get_info(request: Request):
    """Returns models info."""
    res = api.Info(name=request.app.model_name, loaded=False)
    return res
