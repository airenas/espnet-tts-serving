from pydantic.fields import Optional
from pydantic.main import BaseModel


class Info(BaseModel):
    name: Optional[str] = None
    loaded: bool = False


class Input(BaseModel):
    text: str
    model: Optional[str] = None


class Output(BaseModel):
    data: str
    error: Optional[str] = None
