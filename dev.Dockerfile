FROM docker.io/library/golang:alpine AS build-go

RUN go install github.com/air-verse/air@latest

RUN apk update && apk add npm

WORKDIR /app

COPY . .

EXPOSE 8000

VOLUME [ "/data" ]

CMD ["/go/bin/air"]
