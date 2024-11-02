package main

import (
	"crypto/rand"
	"encoding/base64"
	"errors"
	"github.com/sirupsen/logrus"
	"github.com/thechubbypanda/syncify/config"
	"github.com/zmb3/spotify/v2"
	"github.com/zmb3/spotify/v2/auth"
	"golang.org/x/oauth2"
	"net/http"
	"time"
)

var authenticator *spotifyauth.Authenticator

func setAuthenticator(cfg config.Config) {
	authenticator = spotifyauth.New(
		spotifyauth.WithRedirectURL(cfg.Url+"/callback"),
		spotifyauth.WithScopes(spotifyauth.ScopePlaylistReadPrivate, spotifyauth.ScopePlaylistModifyPrivate, spotifyauth.ScopeUserLibraryRead, spotifyauth.ScopePlaylistModifyPublic),
	)
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

	http.Redirect(w, r, authenticator.AuthURL(state), http.StatusSeeOther)
}

func Callback(w http.ResponseWriter, r *http.Request) {
	state := sm.PopString(r.Context(), "state")

	token, err := authenticator.Token(r.Context(), state, r)
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

func GetClient(r *http.Request) (*spotify.Client, error) {
	token, ok := sm.Get(r.Context(), "token").(oauth2.Token)
	if !ok {
		return nil, errors.New("missing token")
	}
	if token.Expiry.Before(time.Now()) {
		return nil, errors.New("token expired")
	}
	return spotify.New(authenticator.Client(r.Context(), &token)), nil
}
