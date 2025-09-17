# AI generated Makefile

.PHONY: help install install-dev test lint format clean setup run-example docker-build docker-up docker-down docker-logs docker-clean

help: ## Show this help message
	@echo "Weather Outfit AI - Development Commands"
	@echo "========================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	uv sync

install-dev: ## Install development dependencies
	uv sync --extra dev

lint: ## Run linting checks
	uv run ruff check weather_outfit_ai/ tests/
	uv run mypy weather_outfit_ai/

format: ## Format code
	uv run black weather_outfit_ai/ tests/
	uv run isort weather_outfit_ai/ tests/
	uv run ruff check --fix weather_outfit_ai/ tests/

clean: ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf htmlcov/
	rm -rf .coverage

dev: ## Start development environment
	uv sync --extra dev
	uv run weather-outfit-ai info

check: ## Run all checks (lint, test, format)
	$(MAKE) lint
	$(MAKE) test
	$(MAKE) format

build: ## Build the package
	uv build

publish: ## Publish to PyPI (requires authentication)
	uv publish

# Docker Commands
docker-build: ## Build Docker containers
	@echo "🐳 Building Docker containers..."
	docker-compose build

docker-up: ## Start all services with Docker
	@echo "🚀 Starting all services with Docker..."
	docker-compose up --build

docker-up-d: ## Start all services in background
	@echo "🚀 Starting all services in background..."
	docker-compose up --build -d

docker-down: ## Stop all Docker services
	@echo "🛑 Stopping all Docker services..."
	docker-compose down

docker-logs: ## Show Docker logs
	@echo "📋 Showing Docker logs..."
	docker-compose logs -f

docker-clean: ## Clean up Docker resources
	@echo "🧹 Cleaning up Docker resources..."
	docker-compose down -v
	docker system prune -f

docker-reset: ## Reset all Docker data (WARNING: Deletes everything)
	@echo "🔄 Resetting all Docker data..."
	docker-compose down -v
	@docker volume rm weather-outfit-ai_chromadb_data weather-outfit-ai_wardrobe_data 2>/dev/null || true
	docker-compose up --build 

## Utility Commands
populate-wardrobe: ## Populate wardrobe with sample data (local development)
	@echo "📦 Populating wardrobe with sample data..."
	cd weather_outfit_ai && python ../utils/populate_wardrobe.py