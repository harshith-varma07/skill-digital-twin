.PHONY: help build up down restart logs clean dev prod test shell db-shell seed backup restore health

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build all Docker images
	docker compose build

up: ## Start all services in detached mode
	docker compose up -d

down: ## Stop all services
	docker compose down

restart: ## Restart all services
	docker compose restart

logs: ## View logs from all services
	docker compose logs -f

logs-backend: ## View backend logs
	docker compose logs -f backend

logs-frontend: ## View frontend logs
	docker compose logs -f frontend

logs-db: ## View database logs
	docker compose logs -f postgres

clean: ## Stop and remove all containers, networks, and volumes
	docker compose down -v

dev: ## Start development environment with hot-reload
	docker compose -f docker-compose.dev.yml up

prod: ## Start production environment
	docker compose up -d

rebuild: ## Rebuild and restart all services
	docker compose up -d --build

rebuild-backend: ## Rebuild and restart backend service
	docker compose up -d --build backend

rebuild-frontend: ## Rebuild and restart frontend service
	docker compose up -d --build frontend

shell: ## Access backend container shell
	docker compose exec backend bash

shell-frontend: ## Access frontend container shell
	docker compose exec frontend sh

db-shell: ## Access PostgreSQL shell
	docker compose exec postgres psql -U postgres -d skill_digital_twin

seed: ## Seed database with initial data
	docker compose exec backend python -m app.seed_data

backup: ## Backup database to backup.sql
	@docker compose ps postgres | grep -q "Up" || (echo "Error: PostgreSQL service is not running. Start it with 'make up'" && exit 1)
	docker compose exec postgres pg_dump -U postgres skill_digital_twin > backup.sql
	@echo "Database backed up to backup.sql"

restore: ## Restore database from backup.sql
	@docker compose ps postgres | grep -q "Up" || (echo "Error: PostgreSQL service is not running. Start it with 'make up'" && exit 1)
	@test -f backup.sql || (echo "Error: backup.sql not found" && exit 1)
	docker compose exec -T postgres psql -U postgres skill_digital_twin < backup.sql
	@echo "Database restored from backup.sql"

ps: ## Show running containers
	docker compose ps

stop-backend: ## Stop backend service
	docker compose stop backend

stop-frontend: ## Stop frontend service
	docker compose stop frontend

start-backend: ## Start backend service
	docker compose start backend

start-frontend: ## Start frontend service
	docker compose start frontend

test: ## Run tests (when implemented)
	@echo "Tests not yet implemented"

status: ## Show status of all services
	@docker compose ps
	@echo ""
	@echo "Volumes:"
	@docker volume ls | grep skill
	@echo ""
	@echo "Networks:"
	@docker network ls | grep skill

health: ## Run health check on all services
	@./healthcheck.sh
