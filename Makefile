.PHONY: $(wildcard *)

deps:
	pip install -r requirements.txt
	cd frontend && pnpm i

# Development commands

frontend:
	cd frontend && pnpm run dev

api:
	python -m uvicorn src.webapp.main:app --reload

worker:
	python -m src.worker.main


# Docker setup commands

network:
	docker network create syncify2 || true


# Database commands

db: network db/kill db/start db/upgrade
db/kill:
	docker rm -f syncify2_db || true
db/start:
	docker run --rm -d -p 5432:5432 --name syncify2_db --network syncify2 -e POSTGRES_USER=syncify2 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=syncify2 postgres:alpine
db/wait:
	while ! docker exec syncify2_db pg_isready -U syncify2; do sleep 1; done
db/upgrade: db/wait
	alembic upgrade head


# Production commands

prod: network db/wait prod/kill prod/build prod/run
prod/build:
	docker buildx build . -t syncify2
prod/run:
	docker run --rm -it -p 5000:5000 --network syncify2 --env-file .env -e DB_HOST=syncify2_db -e HOST=0.0.0.0 --name syncify2 syncify2
prod/kill:
	docker kill syncify2 || true
