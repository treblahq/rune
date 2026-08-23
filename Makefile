.DEFAULT_GOAL := help

BACKEND_HOST ?= 127.0.0.1
BACKEND_PORT ?= 43891
FRONTEND_HOST ?= 127.0.0.1
FRONTEND_PORT ?= 3000
NEXT_PUBLIC_RUNE_API_URL ?= http://$(BACKEND_HOST):$(BACKEND_PORT)

.PHONY: help install setup start dev check clean

help:
	@printf "Rune local commands:\n\n"
	@printf "  install  Install frontend and backend dependencies\n"
	@printf "  start    Start Rune locally\n"
	@printf "  check    Run all quality checks\n"
	@printf "  clean    Remove generated project caches\n"

install:
	$(MAKE) -C backend install
	$(MAKE) -C frontend install

setup: install

start:
	@bash -c 'trap "kill 0" INT TERM EXIT; $(MAKE) -C backend dev HOST=$(BACKEND_HOST) PORT=$(BACKEND_PORT) & $(MAKE) -C frontend dev HOST=$(FRONTEND_HOST) PORT=$(FRONTEND_PORT) NEXT_PUBLIC_RUNE_API_URL=$(NEXT_PUBLIC_RUNE_API_URL) & wait'

dev: start

check:
	$(MAKE) -C backend check
	$(MAKE) -C frontend check

clean:
	$(MAKE) -C backend clean
	$(MAKE) -C frontend clean
