import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("uvicorn.error")


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except ValueError as ve:
            logger.exception(msg=ve.__class__.__name__)
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Bad Request",
                    "message": f"Invalid value: {str(ve)}",
                },
            )
        except PermissionError as pe:
            logger.exception(msg=pe.__class__.__name__)
            return JSONResponse(
                status_code=403,
                content={"error": "Forbidden", "message": "Permission denied."},
            )
        except Exception as e:
            logger.exception(msg=e.__class__.__name__)
            logger.exception(msg=e.__context__)
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred.",
                },
            )
