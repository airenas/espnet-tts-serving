from typing import List

from pydantic.fields import Optional
from pydantic.main import BaseModel


class ModelInfo(BaseModel):
    name: Optional[str] = None
    device: Optional[str] = None


class Info(BaseModel):
    models: List[ModelInfo] = None
    workers: Optional[int] = 0


class Input(BaseModel):
    text: str
    voice: Optional[str] = None


class Output(BaseModel):
    data: str
    error: Optional[str] = None


class Live(BaseModel):
    ok: bool = False
