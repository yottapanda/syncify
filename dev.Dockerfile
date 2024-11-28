FROM docker.io/library/golang:alpine AS build-go

RUN apk update && apk add npm

WORKDIR /app

COPY . .

RUN npm i

CMD ["sh", "-c", "npx tailwindcss -i stylesheet.css -o static/stylesheet.css && go run cmd/main/main.go"]
