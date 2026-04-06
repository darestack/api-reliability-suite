.PHONY: install run test lint format docker-build docker-run stack-up stack-down debug load-test clean

BASE_URL ?= http://localhost:8000
LOAD_TEST_ENV ?= local-docker-compose

install:
	poetry install

run:
	poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

test:
	OTLP_ENDPOINT="" poetry run pytest -v --cov=src --cov-report=term-missing

lint:
	poetry run ruff check .

format:
	poetry run ruff format .

install-hooks:
	poetry run pre-commit install

docker-build:
	docker build -t reliability-suite .

docker-run:
	docker run --env-file .env -p 8000:8000 reliability-suite

stack-up:
	docker compose up -d

stack-down:
	docker compose down

debug:
	docker compose exec api python scripts/cli_debugger.py

load-test:
	k6 run \
		-e BASE_URL=$(BASE_URL) \
		-e ENV_NAME=$(LOAD_TEST_ENV) \
		-e GIT_SHA=$$(git rev-parse --short HEAD)$$(git diff --quiet --ignore-submodules HEAD -- || printf -- '-dirty') \
		-e TEST_DATE=$$(date -u +%F) \
		loadtests/k6/reliability-smoke.js

clean:
	rm -rf .pytest_cache .ruff_cache .coverage htmlcov app.json app.log app.json.* test_app.json
	find . -type d -name "__pycache__" -exec rm -rf {} +
