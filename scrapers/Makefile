.PHONY: default tests coverage lint format types

default: format lint types tests

tests:
	poetry run pytest --cov=.

coverage:
	poetry run coverage xml

lint:
	poetry run flake8

format:
	poetry run black .

types:
	poetry run mypy --install-types --non-interactive ./ep_votes/
