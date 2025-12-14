.PHONY: $(wildcard *)

deps:
	pip install -r requirements.txt
	cd frontend && pnpm i

# Development commands

frontend:
	cd frontend && pnpm run dev

api:
	python -m uvicorn webapp.main:app --reload

worker:
	python -m worker.main


# Docker setup commands

network:
	docker network create syncify || true
	docker volume create syncify_db || true


# Database commands

db: network db/kill db/start db/upgrade
db/kill:
	docker container rm -f syncify_db || true
db/start:
	docker run --rm -d -p 5432:5432 --name syncify_db --network syncify -v syncify_db:/var/lib/postgresql/data -e POSTGRES_PASSWORD=syncify postgres:alpine
db/wait:
	while ! docker exec syncify_db pg_isready -U postgres; do sleep 1; done
db/upgrade: db/wait
	alembic upgrade head


# Production commands

prod: network db/wait prod/kill prod/build prod/run
prod/build:
	docker buildx build . -t syncify
prod/run:
	docker run --rm -it -p 5000:5000 --network syncify --env-file .env -e DB_HOST=syncify_db -e BASE_URI=http://127.0.0.1:5000 --name syncify syncify
prod/kill:
	docker kill syncify2 || true
