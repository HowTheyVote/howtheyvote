default: format-check lint typecheck test

test:
	poetry run pytest --cov=. --cov=!./howtheyvote/alembic --cov-report=html:tests/htmlcov

coverage:
	poetry run coverage xml

lint:
	poetry run ruff check .

lint-fix:
	poetry run ruff check --fix .

format:
	poetry run ruff format .

format-check:
	poetry run ruff format --check .

typecheck:
	poetry run mypy --strict ./howtheyvote/

dev:
	poetry run flask --app howtheyvote.wsgi run --debug --host=0.0.0.0
