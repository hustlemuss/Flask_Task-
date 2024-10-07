import pydantic
from typing import Optional


class HttpError(Exception):
    def __init__(self, status_code: int, message: str | dict | list):
        self.status_sode = status_code
        self.message = message


class PatchAdvt(pydantic.BaseModel):
    title: Optional[str]
    description: Optional[str]
    author: Optional[str]

    @pydantic.validator("description")
    def len_advt(cls, value: str):
        if len(value) <= 1:
            raise ValueError("Объявление слишком короткое")
        return value
