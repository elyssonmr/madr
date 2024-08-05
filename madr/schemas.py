import string
from typing import Annotated

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    EmailStr,
)


def sanitize_name(value: str):
    result = ' '.join(value.split())

    return result.strip(string.punctuation).strip().lower()


class MessageSchema(BaseModel):
    message: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserSchema(BaseModel):
    username: Annotated[str, AfterValidator(sanitize_name)]
    email: EmailStr
    password: str
    model_config = ConfigDict(from_attributes=True)


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)
