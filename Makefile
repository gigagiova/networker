# PostgreSQL Docker configuration
DB_NAME = networker
DB_USER = postgres
DB_PASSWORD = postgres
DB_PORT = 5432
CONTAINER_NAME = networker-postgres

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
	@echo "  make setup-env    - Create .env file from template with correct DB settings"

# Start PostgreSQL in Docker
.PHONY: start
start:
	@echo "Starting PostgreSQL Docker container..."
	@docker ps -q -f name=$(CONTAINER_NAME) > /dev/null || \
	docker run --name $(CONTAINER_NAME) \
		-e POSTGRES_PASSWORD=$(DB_PASSWORD) \
		-e POSTGRES_DB=$(DB_NAME) \
		-p $(DB_PORT):5432 \
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

# Export the DATABASE_URL environment variable
.PHONY: env
env:
	@echo "export DB_NAME=$(DB_NAME)"
	@echo "export DB_USER=$(DB_USER)"
	@echo "export DB_PASSWORD=$(DB_PASSWORD)"
	@echo "export DB_HOST=localhost"
	@echo "export DB_PORT=$(DB_PORT)"
	@echo "export DATABASE_URL=postgresql://$(DB_USER):$(DB_PASSWORD)@localhost:$(DB_PORT)/$(DB_NAME)"
	@echo "export ENVIRONMENT=local"

# Set up .env file from template
.PHONY: setup-env
setup-env:
	@if [ -f .env ]; then \
		echo ".env file already exists. Do you want to overwrite it? (y/n)"; \
		read answer; \
		if [ "$$answer" != "y" ]; then \
			echo "Aborted."; \
			exit 1; \
		fi; \
	fi
	@echo "Creating .env file..."
	@cp .env.example .env
	@sed -i '' 's/DB_NAME=.*/DB_NAME=$(DB_NAME)/g' .env
	@sed -i '' 's/DB_USER=.*/DB_USER=$(DB_USER)/g' .env
	@sed -i '' 's/DB_PASSWORD=.*/DB_PASSWORD=$(DB_PASSWORD)/g' .env
	@sed -i '' 's/DB_PORT=.*/DB_PORT=$(DB_PORT)/g' .env
	@echo "Environment file created successfully"
	@echo "Don't forget to add your API keys in the .env file" 