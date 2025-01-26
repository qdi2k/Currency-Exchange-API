import logging

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings

logger = logging.getLogger()


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """
    ### Общая обработка исключений, вывод заголовков входящего запроса,
        а также вывод подробностей серверной ошибки при включенном DEBUG
    """

    async def dispatch(self, request: Request, call_next):
        try:
            logger.debug(f"Request headers:\n{dict(request.headers)}")
            response = await call_next(request)
            return response
        except HTTPException as http_exc:
            return JSONResponse(
                status_code=http_exc.status_code,
                content={
                    "status": http_exc.status_code,
                    "detail": http_exc.detail,
                },
            )
        except Exception as exc:
            if not settings.DEBUG:
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={
                        "status": "error",
                        "detail": "Internal Server Error",
                    },
                )
            raise exc
