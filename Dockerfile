FROM docker.io/library/node:alpine AS build-frontend

RUN apk add pnpm

WORKDIR /build

COPY frontend .

RUN pnpm i

RUN pnpm run build

# Inspired by https://hynek.me/articles/docker-uv/

FROM ghcr.io/astral-sh/uv:python3.13-alpine AS builder

SHELL ["sh", "-exc"]

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/app

COPY uv.lock uv.lock
COPY pyproject.toml pyproject.toml

RUN --mount=type=cache,target=/root/.cache \
    uv sync --locked --no-dev --no-install-project

COPY . /src

WORKDIR /src

RUN --mount=type=cache,target=/root/.cache \
    uv sync --locked --no-dev --no-editable

FROM python:3.13-alpine

STOPSIGNAL SIGINT

WORKDIR /app

COPY docker-entrypoint.sh /docker-entrypoint.sh

SHELL ["sh", "-exc"]

ENTRYPOINT ["/docker-entrypoint.sh"]

COPY --from=builder /app /app

COPY alembic.ini /app/alembic.ini

COPY --from=build-frontend /build/dist /app/public

ENV WEBSITE_PATH=public

EXPOSE 5000
