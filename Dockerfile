# syntax=docker/dockerfile:1

ARG PYTHON_IMAGE=python:3.12-slim@sha256:3d5ed973e45820f5ba5e46bd065bd88b3a504ff0724d85980dcd05eab361fcf4
ARG APP_UID=10001
ARG APP_GID=10001

# Stage 1: Build
FROM ${PYTHON_IMAGE} AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir poetry==2.2.1

# Copy dependencies file
COPY pyproject.toml poetry.lock* ./

# Install runtime dependencies into an app-local virtualenv so the final image
# does not carry Poetry or builder-only packages.
RUN poetry config virtualenvs.in-project true \
  && poetry install --only main --no-interaction --no-ansi

# Stage 2: Runtime
FROM ${PYTHON_IMAGE}

ARG APP_UID
ARG APP_GID

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
  && apt-get install -y --only-upgrade --no-install-recommends \
    libssl3t64 \
    openssl \
    openssl-provider-legacy \
  && rm -rf /var/lib/apt/lists/*

RUN groupadd --system --gid ${APP_GID} app \
  && useradd --system --uid ${APP_UID} --gid ${APP_GID} --home-dir /app --shell /usr/sbin/nologin app \
  && mkdir -p /app/data /app/scripts \
  && chown -R app:app /app

ENV PATH="/app/.venv/bin:${PATH}"

# Copy the runtime virtualenv from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code and runtime helper scripts
COPY --chown=app:app src/ ./src/
COPY --chown=app:app scripts/ ./scripts/

# Expose port
EXPOSE 8000

USER app

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
