package main

import (
	"encoding/gob"
	"github.com/alexedwards/scs/v2"
	"github.com/alexedwards/scs/v2/memstore"
	"github.com/chi-middleware/logrus-logger"
	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/ilyakaznacheev/cleanenv"
	"github.com/sirupsen/logrus"
	"github.com/thechubbypanda/syncify/views"
	"github.com/zmb3/spotify/v2"
	"github.com/zmb3/spotify/v2/auth"
	"golang.org/x/oauth2"
	"net/http"
	"time"
)

var config Config

var sm = scs.New()

func main() {
	err := cleanenv.ReadEnv(&config)
	if err != nil {
		logrus.Fatalln("error reading config: ", err)
		return
	}

	logrus.SetLevel(config.LogLevel)

	gob.Register(oauth2.Token{})

	SetOauthConfig(config)

	sm.Store = memstore.New()

	sm.Cookie.Secure = false
	sm.Cookie.HttpOnly = true
	sm.Cookie.Persist = false
	sm.Cookie.Name = "syncify_session"
	sm.Cookie.SameSite = http.SameSiteLaxMode

	r := chi.NewRouter()

	r.Use(
		logger.Logger("router", logrus.StandardLogger()),
		middleware.StripSlashes,
		sm.LoadAndSave,
	)

	r.Route("/", func(r chi.Router) {
		r.Get("/", Root)
		r.Get("/sync", Sync)
		r.Get("/login", Login)
		r.Get("/logout", Logout)
		r.Get("/callback", Callback)
		r.Get("/*", http.StripPrefix("/", http.FileServer(http.Dir("static/"))).ServeHTTP)
	})

	logrus.Infoln("starting web server on", "0.0.0.0:8000")
	httpErr := http.ListenAndServe("0.0.0.0:8000", r)
	if httpErr != nil {
		logrus.Errorln(httpErr)
	}
}

func Root(w http.ResponseWriter, r *http.Request) {
	token, ok := sm.Get(r.Context(), "token").(oauth2.Token)
	if !ok || token.Expiry.Before(time.Now()) {
		err := views.Root(nil, -1, nil).Render(w)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		return
	}
	s := spotify.New(spotifyauth.New().Client(r.Context(), &token))

	user, err := s.CurrentUser(r.Context())
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		logrus.Errorln(err)
		return
	}

	err = views.Root(user, -1, nil).Render(w)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
}
