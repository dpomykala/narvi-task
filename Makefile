.PHONY: help, build, up, tests

help:
	@echo "Available targets: build, up, tests"

build:
	docker compose build

up: build
	docker compose up

tests: build
	docker compose run -it --rm app poetry run python manage.py test
