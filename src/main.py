from fastapi import FastAPI
import structlog
import uvicorn
from src.core.logging import configure_logging
# from core.exceptions import global_exception_handler
from src.core.exceptions import GlobalExceptionMiddleware
from src.core.tracing import configure_tracing
import asyncio
from contextlib import asynccontextmanager

# Configure logging
configure_logging()

# Get logger
logger = structlog.get_logger()

# Define lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
  logger.info("startup_event", status="starting_app")
  yield
  logger.info("shutdown_event", status="stopping_app")

# Create FastAPI instance
app = FastAPI(
  title="API Reliability Suite",
  description="A template for robust, debuggable, and maintainable APIs",
  version="1.0.0",
  lifespan=lifespan
)

# Register exception handler
# app.add_exception_handler(Exception, global_exception_handler)

# Register middleware
app.add_middleware(GlobalExceptionMiddleware)

# CONFIGURE TRACING (after app is created, before routes are hit)
configure_tracing(app)

# Health Check
@app.get("/health")
async def health_check():
  logger.info("health_check_called", endpoint="/health")
  return {"status": "ok", "service": "reliability-suite"}

@app.get("/force-error")
async def force_error():
  logger.info("triggering_error")

  return 1/0

@app.get("/slow")
async def slow_endpoint():
  logger.info("slow_endpoint_called")
  await asyncio.sleep(2)
  return {"status": "done", "message": "That was slow!"}

# 
if __name__ == "__main__":
  uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True, log_level="warning")
