.PHONY: install backend frontend dev setup-db migrate

install:
	cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
	cd frontend && npm install

backend:
	cd backend && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev

dev:
	@echo "Run 'make backend' and 'make frontend' in separate terminals"

setup-db:
	cd backend && source venv/bin/activate && alembic upgrade head

migrate:
	cd backend && source venv/bin/activate && alembic revision --autogenerate -m "$(msg)"
