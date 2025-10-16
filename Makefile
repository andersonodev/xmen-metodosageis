# Makefile para Xmen-AgileTeam

.PHONY: help install migrate seed test run docker-build docker-up docker-down clean

# Colors for help
RED=\033[0;31m
GREEN=\033[0;32m
YELLOW=\033[1;33m
NC=\033[0m # No Color

help:  ## Mostra esta ajuda
	@echo "$(GREEN)Comandos disponíveis:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'

install:  ## Instalar dependências
	pip install -r requirements.txt

migrate:  ## Executar migrations
	python manage.py makemigrations
	python manage.py migrate

seed:  ## Povoar banco com dados de exemplo
	python manage.py seed_data

test:  ## Executar testes
	pytest

run:  ## Executar servidor de desenvolvimento
	python manage.py runserver

celery-worker:  ## Executar Celery worker
	celery -A xmen_agileteam worker -l info

celery-beat:  ## Executar Celery beat
	celery -A xmen_agileteam beat -l info

# Docker commands
docker-build:  ## Construir imagens Docker
	docker-compose build

docker-up:  ## Subir containers
	docker-compose up -d

docker-logs:  ## Ver logs dos containers
	docker-compose logs -f

docker-down:  ## Parar containers
	docker-compose down

docker-clean:  ## Limpar containers e volumes
	docker-compose down -v
	docker system prune -f

# Development shortcuts
dev-setup:  ## Setup completo para desenvolvimento
	make install
	make migrate
	make seed

dev-reset:  ## Reset completo do ambiente
	rm -f db.sqlite3
	find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
	find . -path "*/migrations/*.pyc" -delete
	make migrate
	make seed

# Deployment
deploy-check:  ## Verificar se está pronto para deploy
	python manage.py check --deploy
	python manage.py collectstatic --noinput --dry-run

# Documentation
docs:  ## Gerar documentação
	@echo "API Documentation available at:"
	@echo "  Swagger UI: http://localhost:8000/api/docs/"
	@echo "  ReDoc: http://localhost:8000/api/redoc/"

# Quick start
quick-start:  ## Start rápido com Docker
	@echo "$(GREEN)🚀 Iniciando Xmen-AgileTeam...$(NC)"
	make docker-build
	make docker-up
	@echo "$(GREEN)✅ Aplicação rodando em http://localhost:8000$(NC)"
	@echo "$(YELLOW)📚 Documentação: http://localhost:8000/api/docs/$(NC)"
	@echo "$(YELLOW)🌸 Flower (Celery): http://localhost:5555$(NC)"

status:  ## Verificar status dos serviços
	@echo "$(GREEN)📊 Status dos serviços:$(NC)"
	docker-compose ps