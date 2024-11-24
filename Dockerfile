FROM docker.io/library/golang:alpine AS build-go

WORKDIR /build

COPY . .

RUN go build -o out/syncify .

FROM docker.io/library/node:alpine AS build-tailwind

WORKDIR /build

COPY . .

RUN npm i

RUN npm run build-prod

FROM docker.io/library/alpine:latest

WORKDIR /app

COPY static static

COPY --from=build-go /build/out/syncify .

COPY --from=build-tailwind /build/static/stylesheet.css static/

EXPOSE 8000

CMD ["./syncify"]
