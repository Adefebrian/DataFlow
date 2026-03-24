# DataFlow — Docker Commands
# ─────────────────────────────────────────────────────────────────────────────
# Production build (nginx static):   make up
# Dev mode (Vite hot-reload):        make dev
# Stop everything:                   make down
# Rebuild images from scratch:       make rebuild
# View logs:                         make logs
# Shell into api container:          make shell

.PHONY: up dev down rebuild logs shell

## ── Production ───────────────────────────────────────────────────────────────
up:
	docker compose --profile prod up -d --build
	@echo ""
	@echo "  ✅  DataFlow running at http://localhost:3000"
	@echo "      API:      http://localhost:8000"
	@echo "      Login:    admin / admin123"

## ── Development (hot-reload) ─────────────────────────────────────────────────
dev:
	docker compose --profile dev up -d --build
	@echo ""
	@echo "  ✅  DataFlow DEV running at http://localhost:3000 (Vite HMR)"
	@echo "      API:      http://localhost:8000"
	@echo "      Login:    admin / admin123"
	@echo "      Edits to frontend/src/* reload automatically."

## ── Stop all ─────────────────────────────────────────────────────────────────
down:
	docker compose --profile prod --profile dev down

## ── Hard rebuild (no cache) ──────────────────────────────────────────────────
rebuild:
	docker compose --profile prod build --no-cache
	docker compose --profile prod up -d
	@echo "  ✅  Rebuilt and running at http://localhost:3000"

## ── Logs ─────────────────────────────────────────────────────────────────────
logs:
	docker compose logs -f

logs-api:
	docker compose logs -f api

logs-frontend:
	docker compose --profile prod --profile dev logs -f frontend frontend-dev

## ── Shell ────────────────────────────────────────────────────────────────────
shell:
	docker compose exec api bash
