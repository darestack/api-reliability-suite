.PHONY: install run test lint format docker-build docker-run

install:
	poetry install

run:
	poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

test:
	OTLP_ENDPOINT="" poetry run pytest -v

lint:
	poetry run ruff check .

format:
	poetry run ruff format .

install-hooks:
	poetry run pre-commit install

docker-build:
	docker build -t reliability-suite .

docker-run:
	docker run -p 8000:8000 reliability-suite
