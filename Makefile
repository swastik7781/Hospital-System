.PHONY: run test seed migrate docker-up docker-down clean lint

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest -v

seed:
	python scripts/seed.py

migrate:
	alembic upgrade head

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down -v

lint:
	ruff check .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
