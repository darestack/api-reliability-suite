from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger()

class GlobalExceptionMiddleware(BaseHTTPMiddleware):
  async def dispatch(self, request: Request, call_next):
    try:
      return await call_next(request)
    except Exception as exc:
      logger.error(
        "unhandled_exception",
        error=str(exc),
        path=request.url.path,
        method=request.method,
        # exc_info=True # This will include the full traceback in the log
      )
      return JSONResponse(
        status_code=500,
        content={
          "error": "Internal Server Error",
      "message": "An unexpected error occurred. Please contact support.",
      "path": request.url.path
    },
  )