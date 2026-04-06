from fastapi import Request
from fastapi.responses import JSONResponse
import structlog

logger = structlog.get_logger()


async def handle_unexpected_exception(request: Request, exc: Exception):
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
