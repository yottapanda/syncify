FROM docker.io/library/node:alpine AS build-frontend

RUN corepack enable pnpm

WORKDIR /build

COPY frontend .

RUN pnpm i

RUN pnpm run build

FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENV WEBSITE_PATH=frontend/dist

COPY --from=build-frontend /build/dist frontend/dist

EXPOSE 5000

CMD [ "sh", "-c", "python3 -m src.webapp.main" ]
