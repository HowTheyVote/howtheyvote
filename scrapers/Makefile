.PHONY: default tests lint format types

default: format lint types tests

tests:
	poetry run pytest

lint:
	poetry run flake8

format:
	poetry run black .

types:
	poetry run mypy ./ep_votes/
