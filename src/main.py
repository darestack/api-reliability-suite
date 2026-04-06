from fastapi import FastAPI, Request, Depends, HTTPException
from typing import Annotated
import structlog
import uvicorn
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from prometheus_fastapi_instrumentator import Instrumentator

from src.core.logging import configure_logging
from src.core.exceptions import handle_unexpected_exception
from src.core.logs import is_error_log_line
from src.core.middleware import CorrelationIdMiddleware
from src.core.tracing import configure_tracing
from src.core.config import DEFAULT_SECRET_KEY, settings
from src.core.rate_limit import limiter, rate_limit_exceeded_handler
from src.core.llm import summarize_with_llm
from src.domain.models import HealthStatus, Token
from src.services.auth_service import AuthService
from src.infrastructure.user_repository import user_repository
from src.core.circuit_breaker import external_api_breaker
import pybreaker

from slowapi.errors import RateLimitExceeded
from fastapi import Form
from fastapi.security import OAuth2PasswordBearer


# Configure logging
configure_logging()
logger = structlog.get_logger()

# Initialize Services
auth_service = AuthService(repository=user_repository)


# Define lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("startup_event", status="starting_app")
    if settings.SECRET_KEY == DEFAULT_SECRET_KEY:
        logger.warning(
            "default_secret_key_in_use",
            detail="JWT signing is using the demo default. Set SECRET_KEY before shared or production deployments.",
        )
    yield
    logger.info("shutdown_event", status="stopping_app")


# Create FastAPI instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A production-inspired FastAPI template for reliability-focused APIs.",
    version="1.1.0",
    lifespan=lifespan,
)

# Enable Prometheus metrics
Instrumentator().instrument(app).expose(app)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Register Middlewares
app.add_middleware(CorrelationIdMiddleware)  # Traceability first
app.add_exception_handler(Exception, handle_unexpected_exception)

# CONFIGURE TRACING (after app is created, before routes are hit)
configure_tracing(app)


# Health Check
@app.get("/health", response_model=HealthStatus)
@limiter.limit("5/minute")
async def health_check(request: Request):
    logger.info("health_check_called", endpoint="/health")
    return HealthStatus(status="ok", service="reliability-suite")


@app.get("/force-error")
async def force_error():
    logger.info("triggering_error")

    return 1 / 0


@app.get("/slow")
@limiter.limit("10/minute")
async def slow_endpoint(request: Request):
    logger.info("slow_endpoint_called")
    await asyncio.sleep(2)
    return {"status": "done", "message": "That was slow!"}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@app.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login(
    request: Request,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
):
    """
    Login endpoint that returns a JWT token.
    Uses AuthService (Hexagonal Service Layer).
    """
    authenticated = auth_service.authenticate_user(username, password)

    if not authenticated:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    token = auth_service.create_access_token(data={"sub": username})

    return Token(access_token=token, token_type="bearer")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Dependency that validates the JWT and returns the username"""
    return auth_service.verify_token(token)


@app.get("/protected")
async def protected_route(
    request: Request, current_user: str = Depends(get_current_user)
):
    """
    Endpoint that requires a valid JWT token
    """
    logger.info("protected_route_called", user=current_user)
    return {
        "message": f"Hello {current_user}, you are authorized!",
        "user": current_user,
    }


@app.get("/debug/summarize-errors")
@limiter.limit("2/minute")
async def summarize_errors(
    request: Request, current_user: str = Depends(get_current_user)
):
    """
    Analyze local log file and summarize errors using LLM.
    Requires Authentication!
    """
    log_file_path = Path(settings.LOG_FILE_PATH)

    try:
        # Read a snapshot of the current log file. Async iteration against the
        # active rotating log file can stall under this logging setup.
        log_contents = log_file_path.read_text()
    except FileNotFoundError:
        return {"summary": "No log file found.", "provider": None}

    logs = [
        line.strip() for line in log_contents.splitlines() if is_error_log_line(line)
    ]

    if not logs:
        return {"summary": "No errors found in the log file.", "provider": None}

    summary = await summarize_with_llm(logs)
    provider = summary.pop("provider", None)
    return {"ai_summary": summary, "provider": provider}


# Simulation state
SIMULATE_FAILURE = False


@app.post("/simulate-failure/{state}")
async def set_simulate_failure(state: bool):
    """Enable or disable simulated failures for the external service."""
    global SIMULATE_FAILURE
    SIMULATE_FAILURE = state
    return {"message": f"External service failure simulation set to {state}"}


def call_external_service_sync():
    """Logic for calling external service, wrapped by breaker. Synchronous for pybreaker compatibility."""
    if SIMULATE_FAILURE:
        # We must raise a non-HTTPException here to be caught by pybreaker correctly,
        # or we handle it in the endpoint.
        raise ValueError("Simulated External Service Timeout!")

    return {
        "status": "ok",
        "message": "Relay from External API success",
        "source": "upstream",
    }


@app.get("/external-api")
async def external_api():
    """
    Demonstrates:
    1. Circuit Breaker (fault tolerance)
    2. Outgoing Trace Propagation (via instrumented client proxy logic)
    """
    try:
        # Wrap the synchronous logic with the breaker
        result = external_api_breaker.call(call_external_service_sync)
        return result
    except pybreaker.CircuitBreakerError:
        logger.warning("circuit_open_fallback", service="external_api")
        return {
            "status": "degraded",
            "message": "Circuit is OPEN. Returning a degraded fallback response.",
            "source": "fallback",
        }
    except Exception as e:
        logger.error("external_call_failed", error=str(e))
        # Ensure we return 502 as expected by tests for any other failure
        raise HTTPException(status_code=502, detail="External Service Failed")


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app", host="0.0.0.0", port=8000, reload=True, log_level="warning"
    )
