package main

import "github.com/sirupsen/logrus"

type Config struct {
	LogLevel     logrus.Level `env:"LOG_LEVEL" envDefault:"info"`
	ClientID     string       `env:"CLIENT_ID"`
	ClientSecret string       `env:"CLIENT_SECRET"`
	Url          string       `env:"URL"`
}
