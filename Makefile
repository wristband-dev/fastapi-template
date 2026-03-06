# Development Commands
.PHONY: help dev db api frontend start setup stop clean

# =============================================================================
#  HELP
# =============================================================================

help:
	@echo "Development Commands"
	@echo ""
	@echo "  make dev       - Start Docker PostgreSQL + backend API"
	@echo "  make start     - Start backend + frontend together"
	@echo "  make db        - Start Docker PostgreSQL only"
	@echo "  make api       - Start backend API only"
	@echo "  make frontend  - Start frontend only"
	@echo "  make setup     - Install all dependencies (backend + frontend)"
	@echo "  make stop      - Stop all services"
	@echo "  make clean     - Remove venvs, node_modules, docker volumes"
	@echo ""

# =============================================================================
#  DEV - Local Docker PostgreSQL + Backend
# =============================================================================

dev: stop db api

db:
	@cd backend && docker compose up -d
	@echo ""
	@echo "Docker PostgreSQL running on localhost:5433"

api:
	@cd backend && .venv/bin/python run.py

frontend:
	@npm run dev --prefix frontend

# =============================================================================
#  START - Backend + Frontend
# =============================================================================

start: stop db
	@cd backend && .venv/bin/python run.py &
	@sleep 3
	@npm run dev --prefix frontend

# =============================================================================
#  SETUP
# =============================================================================

setup:
	@echo "Installing backend dependencies..."
	@cd backend && python3 -m venv .venv --upgrade-deps && .venv/bin/pip install -e .
	@echo ""
	@echo "Installing frontend dependencies..."
	@npm install --prefix frontend
	@echo ""
	@echo "Setup complete"

# =============================================================================
#  STOP / CLEAN
# =============================================================================

stop:
	@cd backend && docker compose down 2>/dev/null || true

clean: stop
	@cd backend && docker compose down -v 2>/dev/null || true
	@rm -rf backend/.venv
	@find backend -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	@rm -rf frontend/node_modules frontend/.next
	@rm -rf node_modules
	@echo "Clean complete"
