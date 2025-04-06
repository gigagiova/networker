# Include environment variables from .env file
include .env

# Default target
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make start        - Start PostgreSQL in Docker"
	@echo "  make stop         - Stop PostgreSQL container"
	@echo "  make restart      - Restart PostgreSQL container"
	@echo "  make logs         - Show PostgreSQL container logs"
	@echo "  make psql         - Connect to PostgreSQL with psql"
	@echo "  make shell        - Open bash shell in PostgreSQL container"
	@echo "  make status       - Check if PostgreSQL container is running"
	@echo "  make env          - Print database connection environment variables"
	@echo "  make show [table] - Show last 10 rows from specified table"

# Show last 10 rows from specified table
.PHONY: show
show:
	@if [ -z "$(filter-out show,$(MAKECMDGOALS))" ]; then \
		echo "Usage: make show <table_name>"; \
		echo "Example: make show sessions"; \
		exit 1; \
	fi
	@docker exec -i networker-postgres psql -U $(DB_USER) -d $(DB_NAME) -c "SELECT * FROM $(filter-out show,$(MAKECMDGOALS)) ORDER BY id DESC LIMIT 10;"

# Catch table name argument
%:
	@:

# Start PostgreSQL in Docker
.PHONY: start
start:
	@echo "Starting PostgreSQL Docker container..."
	@docker ps -q -f name=$(CONTAINER_NAME) > /dev/null || \
	docker run --name $(CONTAINER_NAME) \
		-e POSTGRES_PASSWORD=$(DB_PASSWORD) \
		-e POSTGRES_DB=$(DB_NAME) \
		-p $(DB_PORT):5433 \
		-v networker-pgdata:/var/lib/postgresql/data \
		-d postgres:14
	@echo "PostgreSQL is running on port $(DB_PORT)"
	@echo "Connection string: postgresql://$(DB_USER):$(DB_PASSWORD)@localhost:$(DB_PORT)/$(DB_NAME)"

# Stop PostgreSQL container
.PHONY: stop
stop:
	@echo "Stopping PostgreSQL container..."
	@docker stop $(CONTAINER_NAME) || true

# Restart PostgreSQL container
.PHONY: restart
restart: stop start

# Show PostgreSQL container logs
.PHONY: logs
logs:
	@docker logs -f $(CONTAINER_NAME)

# Connect to PostgreSQL with psql
.PHONY: psql
psql:
	@docker exec -it $(CONTAINER_NAME) psql -U $(DB_USER) -d $(DB_NAME)

# Open bash shell in container
.PHONY: shell
shell:
	@docker exec -it $(CONTAINER_NAME) bash

# Check if container is running
.PHONY: status
status:
	@docker ps -f name=$(CONTAINER_NAME)

# Add to Makefile
.PHONY: pgadmin
pgadmin:
	docker run --name networker-pgadmin -p 5050:80 \
		-e PGADMIN_DEFAULT_EMAIL=admin@example.com \
		-e PGADMIN_DEFAULT_PASSWORD=admin \
		-d dpage/pgadmin4
	@echo "pgAdmin is running at http://localhost:5050"
	@echo "Login with admin@example.com / admin"
