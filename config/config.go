package config

import "github.com/sirupsen/logrus"

type Config struct {
	LogLevel  logrus.Level `env:"LOG_LEVEL" envDefault:"info"`
	Url       string       `env:"URL" envDefault:"http://localhost:8000"`
	Plausible Plausible
}

type Plausible struct {
	ScriptUrl  string `env:"PLAUSIBLE_SCRIPT_URL" envDefault:""`
	DataDomain string `env:"PLAUSIBLE_DATA_DOMAIN"`
	DataApi    string `env:"PLAUSIBLE_DATA_API"`
	Origin     string `env:"PLAUSIBLE_ORIGIN"`
}
