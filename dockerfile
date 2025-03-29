FROM docker.io/library/node:alpine AS build-tailwind

WORKDIR /build

COPY . .

RUN corepack enable pnpm

RUN pnpm i

RUN pnpm run build

FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml .

RUN pip install .

COPY . .

COPY --from=build-tailwind /build/static/style.css ./static/style.css

VOLUME /data

ENV DB_FILE=/data/db.sqlite

EXPOSE 5000

CMD [ "sh", "-c", "python3 -m webapp.app" ]
