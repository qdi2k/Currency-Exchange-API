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
    email: str
    password: str


class ResponseUserLogin(BaseModel):
    access: str
    refresh: str
