from enum import IntEnum
from typing import List

from pydantic.fields import Optional, Field
from pydantic.main import BaseModel


class ModelInfo(BaseModel):
    name: Optional[str] = None
    device: Optional[str] = None


class Info(BaseModel):
    models: List[ModelInfo] = None
    workers: Optional[int] = 0


class PitchChangeType(IntEnum):
    NONE = 0
    HERTZ = 1
    MULTIPLIER = 2
    SEMITONE = 3


class PitchChange(BaseModel):
    type: PitchChangeType = Field(alias='t')
    value: float = Field(alias='v')


class Input(BaseModel):
    text: str
    voice: Optional[str] = None
    speed_control_alpha: Optional[float] = Field(alias='speedAlpha')
    durations_change: Optional[List[float]] = Field(alias='durationsChange')  # list of float multipliers for durations
    pitch_change: Optional[List[List[PitchChange]]] = Field(alias='pitchChange')  # list of PitchChange objects
    priority: Optional[int] = 0


class Output(BaseModel):
    data: str
    durations: Optional[List[int]]
    silDuration: Optional[int]
    step: Optional[int]
    error: Optional[str] = None


class OutputBin(BaseModel):
    data: bytes
    durations: Optional[List[int]]
    silDuration: Optional[int]
    step: Optional[int]
    error: Optional[str] = None

class Live(BaseModel):
    ok: bool = False
