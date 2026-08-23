.DEFAULT_GOAL := help

PM ?= ../scripts/run-npm.sh
HOST ?= 127.0.0.1
PORT ?= 3000
NEXT_PUBLIC_RUNE_API_URL ?= http://127.0.0.1:43891

.PHONY: help install dev build start test lint typecheck check clean

help:
	@printf "Rune frontend commands:\n\n"
	@printf "  install    Install dependencies\n"
	@printf "  dev        Start the Next.js development server\n"
	@printf "  check      Run tests, lint, typecheck, and build\n"

install:
	$(PM) install

dev:
	NEXT_PUBLIC_RUNE_API_URL=$(NEXT_PUBLIC_RUNE_API_URL) $(PM) run dev -- --hostname $(HOST) --port $(PORT)

build:
	$(PM) run build

start:
	$(PM) run start -- --hostname $(HOST) --port $(PORT)

test:
	$(PM) run test

lint:
	$(PM) run lint

typecheck:
	$(PM) run typecheck

check:
	$(PM) run check

clean:
	$(RM) -r .next coverage
