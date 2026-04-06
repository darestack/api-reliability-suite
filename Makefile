.PHONY: install run test lint format docker-build docker-run clean

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

clean:
	rm -rf .pytest_cache .ruff_cache .coverage htmlcov app.json app.log app.json.* test_app.json
	find . -type d -name "__pycache__" -exec rm -rf {} +
