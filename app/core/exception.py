from fastapi import HTTPException
from pydantic import BaseModel
from starlette import status


credentials_auth_email_already = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Пользователь с таким Email уже существует"
)
credentials_wrong_key_accept = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Неверный ключ подтверждения"
)
credentials_refresh_user_accepted = HTTPException(
    status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
    detail="Этот пользователь уже подтвердил свой аккаунт"
)
credentials_not_found_user_with_email = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Пользователь с таким Email не найден"
)
credentials_wrong_password = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Неверный пароль",
)
credentials_token_err = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Неверный или истёкший токен",
    headers={"Authenticate": "Bearer"},
)


class GlobalTypeError(BaseModel):
    """Основной наследуемый класс ошибок"""

    detail: str


class UnauthorizedError(GlobalTypeError):

    detail: str = "Не удалось пройти авторизацию"


class NotFountError(GlobalTypeError):

    detail: str = "Запрашиваемый вами ресурс не найден"


class MethodNotAllowedError(GlobalTypeError):

    detail: str = "Метод запрещен"


class ConflictError(GlobalTypeError):

    detail: str = "Конфликт запроса"


class BadRequestError(GlobalTypeError):

    detail: str = "Ошибка на стороне клиента"


class ForbiddenError(GlobalTypeError):

    detail: str = """Доступ к запрашиваемому ресурсу запрещён"""


class LockedError(GlobalTypeError):
    """Ошибка формат содержимого запроса не поддерживается"""

    detail: str = """Ресурс заблокирован"""


class ErrorDescriptions:
    """Нормализация вида выдаваемых исключений для документации"""

    @staticmethod
    def get_error_for_documentation(
            status_code: int, model_error: GlobalTypeError
    ):
        return {
            status_code: {
                "model": model_error, "description": model_error.detail
            }
        }

    def unauthorized_entity(self):
        return self.get_error_for_documentation(
            status_code=status.HTTP_401_UNAUTHORIZED,
            model_error=UnauthorizedError()
        )

    def not_found_entity(self):
        return self.get_error_for_documentation(
            status_code=status.HTTP_404_NOT_FOUND,
            model_error=NotFountError()
        )

    def method_not_allowed_entity(self):
        return self.get_error_for_documentation(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            model_error=MethodNotAllowedError()
        )

    def conflict_entity(self):
        return self.get_error_for_documentation(
            status_code=status.HTTP_409_CONFLICT,
            model_error=ConflictError()
        )

    def bad_request_entity(self):
        return self.get_error_for_documentation(
            status_code=status.HTTP_400_BAD_REQUEST,
            model_error=BadRequestError()
        )

    def forbidden_entity(self):
        return self.get_error_for_documentation(
            status_code=status.HTTP_403_FORBIDDEN,
            model_error=ForbiddenError()
        )

    def locked_entity(self):
        return self.get_error_for_documentation(
            status_code=status.HTTP_423_LOCKED,
            model_error=LockedError()
        )


responses_err = ErrorDescriptions()