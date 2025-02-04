import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.api.schemas.validators import password_validator


class RequestUserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., max_length=100)
    password: str = Field(..., max_length=64)

    @field_validator("password")
    def validate_password(cls, value):
        return password_validator(value=str(value))


class ResponseUserCreate(BaseModel):
    message: str = ("Мы отправили письмо по адресу user@example.com"
                    + " Нажмите на ссылку внутри, чтобы начать.")


class RequestUserLogin(BaseModel):
    email: EmailStr
    password: str


class ResponseUserLogin(BaseModel):
    token: str


class ResponseAcceptUser(BaseModel):
    message: str = "Поздравляем с успешной регистрацией!"
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
