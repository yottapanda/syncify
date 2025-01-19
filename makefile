.PHONY: dev build prod

# Development commands

dev:
	flask --app webapp/app.py run --debug

# Production commands

prod: build run
build:
	docker build -t syncify2 .
run:
	docker run --rm -d -p 5000:5000 --env-file .env --name syncify2 syncify2
kill:
	docker kill syncify2
