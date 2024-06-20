package config

import "github.com/sirupsen/logrus"

type Config struct {
	LogLevel     logrus.Level `env:"LOG_LEVEL" envDefault:"info"`
	ClientID     string       `env:"CLIENT_ID"`
	ClientSecret string       `env:"CLIENT_SECRET"`
	Url          string       `env:"URL"`
	Plausible    Plausible
}

type Plausible struct {
	ScriptUrl  string `env:"PLAUSIBLE_SCRIPT_URL" envDefault:""`
	DataDomain string `env:"PLAUSIBLE_DATA_DOMAIN"`
	DataApi    string `env:"PLAUSIBLE_DATA_API"`
	Origin     string `env:"PLAUSIBLE_ORIGIN"`
}
