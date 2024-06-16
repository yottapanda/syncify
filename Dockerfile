FROM docker.io/library/golang:alpine as build

WORKDIR /build

COPY . .

RUN go build -o out/spotisync .

FROM docker.io/library/alpine:latest

WORKDIR /app

COPY --from=build /build/out/spotisync /bin/

COPY static static

CMD ["spotisync"]
