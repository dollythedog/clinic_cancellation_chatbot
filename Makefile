# ---------------------------------------------------------------------
# 🏥 Makefile — clinic_cancellation_chatbot
# ---------------------------------------------------------------------
# Usage: run `make help` to list available commands.
# ---------------------------------------------------------------------
# Run "make help" to see available targets.
MAKEFLAGS += --no-print-directory
.SILENT:
SHELL := powershell.exe
.SHELLFLAGS := -NoProfile -Command

# ---------------------------------------------------------------------
# Paths and Environment
# ---------------------------------------------------------------------

PROJECT_DIR := $(shell pwd)
VENV ?= venv
PYTHON := $(VENV)/Scripts/python.exe
PIP := $(VENV)/Scripts/pip.exe

# Variables for file and commit message
FILE ?=
MSG ?=

# ---------------------------------------------------------------------
# PHONY targets
# ---------------------------------------------------------------------
.PHONY: help venv install \
        run-api run-dashboard \
        test test-cov test-watch \
        lint format typecheck quality \
        db-init db-upgrade db-downgrade db-migrate \
        git-pull git-push git-status \
        clean clean-pycache clean-all

# ---------------------------------------------------------------------
# 🧭 HELP
# ---------------------------------------------------------------------

help:
	@echo "=============== clinic_cancellation_chatbot ==============="
	@echo ""
	@echo "Setup:"
	@echo "  make venv                  Create local Python virtual environment"
	@echo "  make install               Install all Python dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make run-api               Start FastAPI backend (with reload)"
	@echo "  make run-dashboard         Start Streamlit dashboard"
	@echo ""
	@echo "Testing:"
	@echo "  make test                  Run all tests"
	@echo "  make test-cov              Run tests with coverage report"
	@echo "  make test-watch            Run tests in watch mode"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint                  Run flake8 linting"
	@echo "  make format                Format code with black and isort"
	@echo "  make typecheck             Run mypy type checking"
	@echo "  make quality               Run all quality checks (lint + typecheck)"
	@echo ""
	@echo "Database:"
	@echo "  make db-init               Initialize database (when implemented)"
	@echo "  make db-upgrade            Apply all migrations"
	@echo "  make db-downgrade          Rollback one migration"
	@echo "  make db-migrate MSG='...'  Create new migration"
	@echo ""
	@echo "Git / Maintenance:"
	@echo "  make git-pull              Pull latest changes from GitHub"
	@echo "  make git-push MSG='msg'    Add, commit, and push changes"
	@echo "  make git-status            Show git status"
	@echo "  make clean                 Remove Python caches"
	@echo "  make clean-all             Deep clean (caches + venv)"
	@echo "==========================================================="

# ---------------------------------------------------------------------
# 🐍 Python environment
# ---------------------------------------------------------------------

venv:
	@echo "[INFO] Creating virtual environment..."
	python -m venv $(VENV)
	@echo "[INFO] Virtual environment created at $(VENV)"

install: venv
	@echo "[INFO] Upgrading pip..."
	$(PIP) install --upgrade pip
	@echo "[INFO] Installing dependencies..."
	$(PIP) install -r requirements.txt
	@echo "[INFO] Installation complete"

# ---------------------------------------------------------------------
# 🚀 Development servers
# ---------------------------------------------------------------------

run-api:
	@echo "[INFO] Starting FastAPI backend on http://0.0.0.0:8000 ..."
	$(PYTHON) -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

run-dashboard:
	@echo "[INFO] Starting Streamlit dashboard on http://localhost:8501 ..."
	$(PYTHON) -m streamlit run dashboard/app.py

# ---------------------------------------------------------------------
# 🧪 Testing
# ---------------------------------------------------------------------

test:
	@echo "[INFO] Running tests..."
	$(PYTHON) -m pytest

test-cov:
	@echo "[INFO] Running tests with coverage..."
	$(PYTHON) -m pytest --cov=app --cov=utils --cov-report=html --cov-report=term
	@echo "[INFO] Coverage report generated at htmlcov/index.html"

test-watch:
	@echo "[INFO] Running tests in watch mode..."
	$(PYTHON) -m pytest-watch

# ---------------------------------------------------------------------
# 🎨 Code Quality
# ---------------------------------------------------------------------

lint:
	@echo "[INFO] Running flake8..."
	$(PYTHON) -m flake8 app/ dashboard/ utils/ tests/

format:
	@echo "[INFO] Formatting code with black..."
	$(PYTHON) -m black app/ dashboard/ utils/ tests/
	@echo "[INFO] Sorting imports with isort..."
	$(PYTHON) -m isort app/ dashboard/ utils/ tests/
	@echo "[INFO] Code formatting complete"

typecheck:
	@echo "[INFO] Running mypy type checking..."
	$(PYTHON) -m mypy app/ utils/

quality: lint typecheck
	@echo "[INFO] All quality checks complete"

# ---------------------------------------------------------------------
# 🗄️ Database commands
# ---------------------------------------------------------------------

db-init:
	@echo "[INFO] Initializing database..."
	$(PYTHON) scripts/init_db.py
	@echo "[INFO] Running migrations..."
	$(PYTHON) -m alembic upgrade head

db-upgrade:
	@echo "[INFO] Applying migrations..."
	$(PYTHON) -m alembic upgrade head

db-downgrade:
	@echo "[INFO] Rolling back one migration..."
	$(PYTHON) -m alembic downgrade -1

db-migrate:
	@if ("$(MSG)" -eq "") { echo "[ERROR] Must pass MSG='migration description'"; exit 1 }
	@echo "[INFO] Creating new migration: $(MSG)"
	$(PYTHON) -m alembic revision --autogenerate -m "$(MSG)"

# ---------------------------------------------------------------------
# 🔧 Git & Cleanup
# ---------------------------------------------------------------------

git-pull:
	@echo "[INFO] Pulling latest changes from GitHub..."
	git pull
	@echo "[INFO] Pull complete"

git-push:
	@if ("$(MSG)" -eq "") { echo "[ERROR] Must pass MSG='commit message'"; exit 1 }
	@echo "[INFO] Adding all changes..."
	git add .
	@echo "[INFO] Committing with message: $(MSG)"
	git commit -m "$(MSG)"
	@echo "[INFO] Pushing to GitHub..."
	git push origin main
	@echo "[INFO] Push complete"

git-status:
	@git status

clean:
	@echo "[INFO] Cleaning Python caches..."
	Get-ChildItem -Path . -Include __pycache__,*.pyc,.pytest_cache,.mypy_cache -Recurse -Force | Remove-Item -Force -Recurse
	@echo "[INFO] Clean complete"

clean-pycache:
	@echo "[INFO] Removing __pycache__ directories..."
	Get-ChildItem -Path . -Include __pycache__ -Recurse -Force | Remove-Item -Force -Recurse

clean-all: clean
	@echo "[INFO] Removing virtual environment..."
	Remove-Item -Path $(VENV) -Recurse -Force -ErrorAction SilentlyContinue
	@echo "[INFO] Deep clean complete"
