package auth

import (
	"errors"
	"github.com/thechubbypanda/syncify/internal/session"
	"github.com/zmb3/spotify/v2"
	"golang.org/x/oauth2"
	"net/http"
	"time"
)

func GetClient(r *http.Request) (*spotify.Client, error) {
	token, ok := session.Manager.Get(r.Context(), "token").(oauth2.Token)
	if !ok {
		return nil, errors.New("missing token")
	}
	if token.Expiry.Before(time.Now()) {
		return nil, errors.New("token expired")
	}
	return spotify.New(Authenticator.Client(r.Context(), &token)), nil
}
