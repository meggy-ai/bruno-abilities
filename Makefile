.PHONY: help install install-dev test test-cov lint format type-check clean docs

help:
	@echo "Available commands:"
	@echo "  make install       Install package"
	@echo "  make install-dev   Install with dev dependencies"
	@echo "  make test          Run tests"
	@echo "  make test-cov      Run tests with coverage"
	@echo "  make lint          Run linters"
	@echo "  make format        Format code"
	@echo "  make type-check    Run type checking"
	@echo "  make clean         Clean build artifacts"
	@echo "  make docs          Build documentation"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev,docs]"

test:
	pytest

test-cov:
	pytest --cov=bruno_abilities --cov-report=term-missing --cov-report=html

lint:
	ruff check bruno_abilities tests
	bandit -r bruno_abilities

format:
	black bruno_abilities tests
	isort bruno_abilities tests

type-check:
	mypy bruno_abilities

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docs:
	cd docs && make html
