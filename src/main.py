from fastapi import FastAPI, Request
import structlog
import uvicorn
from src.core.logging import configure_logging

# from core.exceptions import global_exception_handler
from src.core.exceptions import GlobalExceptionMiddleware
from src.core.tracing import configure_tracing
import asyncio
from contextlib import asynccontextmanager
from src.core.config import settings
from src.core.rate_limit import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException
from src.core.auth import create_access_token, verify_password, get_password_hash
from jose import jwt, JWTError
from src.core.auth import ALGORITHM
from prometheus_fastapi_instrumentator import Instrumentator
from src.core.llm import summarize_with_llm
import aiofiles


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
    title=settings.PROJECT_NAME,
    description="A template for robust, debuggable, and maintainable APIs",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable Prometheus metrics
Instrumentator().instrument(app).expose(app)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Register exception handler
# app.add_exception_handler(Exception, global_exception_handler)

# Register middleware
app.add_middleware(GlobalExceptionMiddleware)

# CONFIGURE TRACING (after app is created, before routes are hit)
configure_tracing(app)


# Health Check
@app.get("/health")
@limiter.limit("5/minute")
async def health_check(request: Request):
    logger.info("health_check_called", endpoint="/health")
    return {"status": "ok", "service": "reliability-suite"}


@app.get("/force-error")
async def force_error():
    logger.info("triggering_error")

    return 1 / 0


@app.get("/slow")
async def slow_endpoint():
    logger.info("slow_endpoint_called")
    await asyncio.sleep(2)
    return {"status": "done", "message": "That was slow!"}


FAKE_USER = {"username": "demo", "hashed_password": get_password_hash("secret123")}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login endpoint that returns a JWT token
    """
    if form_data.username != FAKE_USER["username"]:
        raise HTTPException(status_code=400, detail="Incorrect username")

    if not verify_password(form_data.password, FAKE_USER["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect password")

    token = create_access_token(data={"sub": form_data.username})

    return {"access_token": token, "token_type": "bearer"}


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Dependency that validates the JWT and returns the username"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/protected")
async def protected_route(current_user: str = Depends(get_current_user)):
    """This route requires a valid JWT token"""
    return {"message": f"Hello, {current_user}! You accessed a protected route."}


#
@app.get("/debug/summarize-errors")
async def summarize_errors(current_user: str = Depends(get_current_user)):
    """
    (Admin only) Reads the last 100 lines of app.json and asks AI to summarize errors.
      Requires Authentication!
    """
    log_file_path = "app.json"  # Inspect your local log file
    logs = []

    try:
        async with aiofiles.open(log_file_path, mode="r") as file:
            async for line in file:
                if "error" in line.lower() or "exception" in line.lower():
                    logs.append(line.strip())

    except FileNotFoundError:
        return {"summary": "No log file found."}

    if not logs:
        return {"summary": "No errors found in the log file."}

    summary = await summarize_with_llm(logs)
    return {"ai_summary": summary, "provider": "Auto-Selected"}


#
if __name__ == "__main__":
    uvicorn.run(
        "src.main:app", host="0.0.0.0", port=8000, reload=True, log_level="warning"
    )
