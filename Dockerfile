FROM docker.io/library/golang:alpine as build

WORKDIR /build

COPY . .

RUN go build -o out/syncify .

FROM docker.io/library/alpine:latest

WORKDIR /app

COPY --from=build /build/out/syncify /bin/

COPY static static

CMD ["syncify"]
