from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger()


class GlobalExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except HTTPException as exc:
            # Manually return JSON response for HTTPException to avoid Starlette/BaseHTTPMiddleware issues
            return JSONResponse(
                status_code=exc.status_code,
                content={"error": exc.detail, "path": request.url.path},
            )
        except Exception as exc:
            logger.error(
                "unhandled_exception",
                error=str(exc),
                path=request.url.path,
                method=request.method,
            )
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred. Please contact support.",
                    "path": request.url.path,
                },
            )
