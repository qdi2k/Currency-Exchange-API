import datetime

from pydantic import BaseModel, EmailStr


class RequestUserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str


class ResponseUserCreate(BaseModel):
    id: int
    email: EmailStr
    username: str
    data_register: datetime.datetime


class RequestUserLogin(BaseModel):
    email: EmailStr
    password: str


class ResponseUserLogin(BaseModel):
    token: str


class UserSchema(BaseModel):
    id: int
    email: EmailStr
    username: str
    password: str
    verified: bool
    verification_token: str
    data_register: datetime.datetime

    class Config:
        from_attributes = True
