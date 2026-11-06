from pydantic import BaseModel, Field
from typing import Literal
class SupportAnswer(BaseModel):
    answer:str
    sources:list[str]=Field(default_factory=list)
    confidence:Literal['high','partial','none']='none'
    answered:bool=False
