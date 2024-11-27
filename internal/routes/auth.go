package routes

import (
	"github.com/sirupsen/logrus"
	"github.com/thechubbypanda/syncify/internal/auth"
	"github.com/thechubbypanda/syncify/internal/session"
	"net/http"
)

func Login(w http.ResponseWriter, r *http.Request) {
	state, err := auth.RandomState()
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		logrus.Errorln(err.Error())
		return
	}

	session.Manager.Put(r.Context(), "state", state)

	http.Redirect(w, r, auth.Authenticator.AuthURL(state), http.StatusSeeOther)
}

func Callback(w http.ResponseWriter, r *http.Request) {
	state := session.Manager.PopString(r.Context(), "state")

	token, err := auth.Authenticator.Token(r.Context(), state, r)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		logrus.Errorln(err)
		return
	}

	session.Manager.Put(r.Context(), "token", token)

	http.Redirect(w, r, "/", http.StatusFound)
}

func Logout(w http.ResponseWriter, r *http.Request) {
	session.Manager.Pop(r.Context(), "token")
	http.Redirect(w, r, "/", http.StatusFound)
}
