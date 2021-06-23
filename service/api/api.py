from pydantic.fields import Optional, Field
from pydantic.main import BaseModel


class Info(BaseModel):
    name: Optional[str] = None
    device: Optional[str] = None
    loaded: bool = False


class Input(BaseModel):
    text: str
    model: Optional[str] = None
    speed_control_alpha: Optional[float] = Field(alias='speedAlpha')


class Output(BaseModel):
    data: str
    error: Optional[str] = None
