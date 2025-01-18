package main

import (
	"encoding/gob"
	"github.com/sirupsen/logrus"
	"github.com/yottapanda/syncify/internal/auth"
	"github.com/yottapanda/syncify/internal/config"
	"github.com/yottapanda/syncify/internal/routes"
	"github.com/yottapanda/syncify/internal/session"
	"golang.org/x/oauth2"
	"net/http"
)

func main() {
	config.LoadConfig()

	logrus.SetLevel(config.Cfg.LogLevel)

	auth.InitAuthenticator(&config.Cfg)

	gob.Register(oauth2.Token{})

	session.InitManager(&config.Cfg)

	r := routes.CreateRouter(&config.Cfg)

	logrus.Infoln("starting web server on", ":8000")
	httpErr := http.ListenAndServe(":8000", r)
	if httpErr != nil {
		logrus.Errorln(httpErr)
	}
}
