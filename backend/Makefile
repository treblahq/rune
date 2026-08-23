.DEFAULT_GOAL := help

UV ?= uv
PYTHON_VERSION ?= 3.13
HOST ?= 127.0.0.1
PORT ?= 43891

.PHONY: help install dev test lint format-check typecheck check clean

help:
	@printf "Rune backend commands:\n\n"
	@printf "  install    Install Python and dependencies\n"
	@printf "  dev        Start the loopback FastAPI service\n"
	@printf "  check      Run formatting, lint, types, and tests\n"

install:
	$(UV) sync --python $(PYTHON_VERSION) --extra transcription

dev:
	@if test -x .venv/bin/uvicorn; then .venv/bin/uvicorn app.main:app --host $(HOST) --port $(PORT) --reload; else $(UV) run uvicorn app.main:app --host $(HOST) --port $(PORT) --reload; fi

test:
	@if test -x .venv/bin/pytest; then .venv/bin/pytest; else $(UV) run pytest; fi

lint:
	@if test -x .venv/bin/ruff; then .venv/bin/ruff check app tests; else $(UV) run ruff check app tests; fi

format-check:
	@if test -x .venv/bin/ruff; then .venv/bin/ruff format --check app tests; else $(UV) run ruff format --check app tests; fi

typecheck:
	@if test -x .venv/bin/mypy; then .venv/bin/mypy app; else $(UV) run mypy app; fi

check: format-check lint typecheck test

clean:
	$(RM) -r .venv .pytest_cache .ruff_cache .mypy_cache
