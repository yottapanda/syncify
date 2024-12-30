FROM docker.io/library/node:alpine AS build-tailwind

WORKDIR /build

COPY . .

RUN corepack enable pnpm

RUN pnpm i

RUN pnpx tailwindcss -i tailwind.css -o static/stylesheet.css -m

FROM docker.io/library/golang:alpine AS build-go

WORKDIR /build

COPY . .

COPY --from=build-tailwind /build/static/stylesheet.css static/

RUN go build -o out/syncify cmd/main/main.go

FROM docker.io/library/alpine:latest

WORKDIR /app

COPY --from=build-go /build/out/syncify .

EXPOSE 8000

CMD ["./syncify"]
