from typing import List

from pydantic.fields import Optional, Field
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
    speed_control_alpha: Optional[float] = Field(alias='speedAlpha')
    priority: Optional[int] = 0


class Output(BaseModel):
    data: str
    durations: Optional[List[int]]
    silDuration: Optional[int]
    error: Optional[str] = None


class Live(BaseModel):
    ok: bool = False
