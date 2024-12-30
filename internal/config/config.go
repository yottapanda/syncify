package config

import (
	"github.com/ilyakaznacheev/cleanenv"
	"github.com/joho/godotenv"
	"github.com/sirupsen/logrus"
	"os"
)

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

var Cfg Config

func LoadConfig() {
	if _, err := os.Stat(".env"); err != nil {
		logrus.Infoln("skipped loading .env file:", err)
	} else {
		if err := godotenv.Load(); err != nil {
			logrus.Fatalln("error loading .env file: ", err)
			return
		}
	}

	err := cleanenv.ReadEnv(&Cfg)
	if err != nil {
		logrus.Fatalln("error reading cfg: ", err)
		return
	}
}
