import datetime

from pydantic import BaseModel, EmailStr


class UserData(BaseModel):
    id: int
    email: EmailStr
    username: str
    data_register: datetime.datetime


class RequestUserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str


class ResponseUserCreate(UserData):
    pass


class RequestUserLogin(BaseModel):
    email: EmailStr
    password: str


class ResponseUserLogin(BaseModel):
    token: str
