# 🚀 Document Chat Assistant Makefile
#-----------------------------------------------
# 🐳 Docker Commands - Local Environment
#-----------------------------------------------

# 🏗️ Build all containers for local development
build:
	docker compose -f docker-compose.local.yml build

# 🚀 Start all services in detached mode for local development
up:
	docker compose -f docker-compose.local.yml up -d

# 🛑 Stop and remove all containers for local development
down:
	docker compose -f docker-compose.local.yml down

# ⏹️ Stop all services without removing them for local development
stop:
	docker compose -f docker-compose.local.yml stop

# 🔄 Restart all services for local development
restart:
	docker compose -f docker-compose.local.yml restart

#-----------------------------------------------
# 📊 Logging & Debugging
#-----------------------------------------------

# 📝 View logs for a specific service
log:
	@echo '🔍 Enter service name (e.g., pdf-service, auth-service): '; \
	read SERVICE; \
	docker compose -f docker-compose.local.yml logs -f $$SERVICE

# 🖥️ Open a bash shell in a container
bash:
	@echo '🔍 Enter service name (e.g., pdf-service, auth-service): '; \
	read SERVICE; \
	docker compose -f docker-compose.local.yml exec $$SERVICE bash

# 🐞 Run a service in debug mode with ports exposed
run-debug:
	@echo '🔍 Enter service name (e.g., pdf-service, auth-service): '; \
	read SERVICE; \
	docker compose -f docker-compose.local.yml stop $$SERVICE; \
	docker compose -f docker-compose.local.yml rm -f $$SERVICE; \
	docker compose -f docker-compose.local.yml run --rm --service-ports $$SERVICE

#-----------------------------------------------
# 🗄️ Database Migration Commands
#-----------------------------------------------

# 📝 Create a new migration
makemigrations:
	@echo '✏️ Migration Name: '; \
	read NAME; \
	docker compose run --rm pdf-service alembic -c /app/libs/alembic.ini revision --autogenerate -m "$$NAME"

# ⬆️ Apply all migrations
migrate:
	docker compose run --rm pdf-service alembic -c /app/libs/alembic.ini upgrade heads

# 📋 Show migration history
showmigrations:
	docker compose run --rm pdf-service alembic -c /app/libs/alembic.ini history

# 🏁 Initialize migrations
initmigrations:
	docker compose run --rm pdf-service alembic -c /app/libs/alembic.ini init migrations

# ⬇️ Downgrade to a previous migration
downgrade:
	@echo '⏮️ Enter revision (or press enter for -1): '; \
	read REVISION; \
	if [ -z "$$REVISION" ]; then \
		docker compose run --rm pdf-service alembic -c /app/libs/alembic.ini downgrade -1; \
	else \
		docker compose run --rm pdf-service alembic -c /app/libs/alembic.ini downgrade $$REVISION; \
	fi

#-----------------------------------------------
# 🛠️ Development Tools
#-----------------------------------------------

# 🔍 Set up pre-commit hooks
pre-commit-install:
	pre-commit uninstall && \
	pre-commit install && \
	pre-commit autoupdate && \
	pre-commit install --hook-type commit-msg -f

# 🐚 Open a Python shell in a service
service-shell:
	@echo '🔍 Enter service name (e.g., pdf-service, auth-service): '; \
	read SERVICE; \
	docker compose -f docker-compose.local.yml run --rm $$SERVICE python /app/libs/shell_plus.py
