package routes

import (
	"github.com/sirupsen/logrus"
	"github.com/thechubbypanda/syncify/internal/auth"
	"github.com/thechubbypanda/syncify/internal/config"
	"github.com/thechubbypanda/syncify/internal/model"
	"github.com/thechubbypanda/syncify/internal/views"
	"net/http"
)

func Root(w http.ResponseWriter, r *http.Request) {
	s, err := auth.GetClient(r)
	if err != nil {
		logrus.Debugln(err)
		err := views.Root(model.Model{Plausible: &config.Cfg.Plausible}).Render(w)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			logrus.Errorln(err)
		}
		return
	}
	user, err := s.CurrentUser(r.Context())
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		logrus.Errorln(err)
		return
	}

	err = views.Root(model.Model{
		Plausible: &config.Cfg.Plausible,
		User:      user,
	}).Render(w)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		logrus.Errorln(err)
		return
	}
}
