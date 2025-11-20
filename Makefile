# Omniverse Market API Makefile
# Author: Abhi

.PHONY: help install run test lint gen-sample clean dev

help:  ## Show this help message
	@echo "Omniverse Market API - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	pip install -r requirements.txt
	pre-commit install

run:  ## Run the API server
	uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

test:  ## Run tests
	pytest tests/ -v

lint:  ## Run code quality checks
	black --check .
	isort --check-only .
	flake8 .

format:  ## Format code
	black .
	isort .

gen-sample:  ## Generate sample data
	python data/gen_sample.py

demo:  ## Run demo prediction script
	python run_demo.py

dev:  ## Setup development environment
	make install
	make gen-sample
	@echo "Development environment ready!"
	@echo "Run 'make run' to start the API server"

clean:  ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/

check:  ## Run all quality checks
	make lint
	make test

ci:  ## Run CI pipeline (lint + test)
	make lint
	make test