FROM docker.io/library/golang:alpine as build-go

WORKDIR /build

COPY . .

RUN go build -o out/syncify .

FROM docker.io/library/node:alpine as build-tailwind

WORKDIR /build

COPY . .

RUN npm i

RUN npx tailwindcss -i stylesheet.css -o static/stylesheet.css

FROM docker.io/library/alpine:latest

WORKDIR /app

COPY --from=build-go /build/out/syncify /bin/

COPY --from=build-tailwind /build/static static

CMD ["syncify"]
