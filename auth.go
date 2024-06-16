package main

import (
	"crypto/rand"
	"encoding/base64"
	"github.com/sirupsen/logrus"
	"golang.org/x/oauth2"
	"net/http"
	"os"
	"strings"
)

var oauthConfig = oauth2.Config{
	ClientID:     os.Getenv("CLIENT_ID"),
	ClientSecret: os.Getenv("CLIENT_SECRET"),
	Endpoint: oauth2.Endpoint{
		AuthURL:       "https://accounts.spotify.com/authorize",
		DeviceAuthURL: "",
		TokenURL:      "https://accounts.spotify.com/api/token",
		AuthStyle:     0,
	},
	RedirectURL: strings.Join([]string{os.Getenv("URL"), "callback"}, "/"),
	Scopes:      []string{"user-library-read", "playlist-read-public", "playlist-modify-public"},
}

func randomState() (string, error) {
	var bytes = make([]byte, 32)
	_, err := rand.Read(bytes)
	if err != nil {
		return "", err
	}
	return base64.URLEncoding.EncodeToString(bytes), nil
}

func Login(w http.ResponseWriter, r *http.Request) {
	state, err := randomState()
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		logrus.Errorln(err.Error())
		return
	}

	sm.Put(r.Context(), "state", state)

	http.Redirect(w, r, oauthConfig.AuthCodeURL(state), http.StatusSeeOther)
}

func Callback(w http.ResponseWriter, r *http.Request) {
	state := sm.PopString(r.Context(), "state")
	if state == "" || r.URL.Query().Get("state") != state {
		http.Redirect(w, r, "/login", http.StatusTemporaryRedirect)
		logrus.Traceln("state did not match:", state)
		return
	}

	token, err := oauthConfig.Exchange(r.Context(), r.URL.Query().Get("code"))
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		logrus.Errorln(err)
		return
	}

	sm.Put(r.Context(), "token", token)

	http.Redirect(w, r, "/", http.StatusFound)
}

func Logout(w http.ResponseWriter, r *http.Request) {
	sm.Pop(r.Context(), "token")
	http.Redirect(w, r, "/", http.StatusFound)
}
