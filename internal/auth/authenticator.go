package auth

import (
	"github.com/thechubbypanda/syncify/internal/config"
	"github.com/zmb3/spotify/v2/auth"
)

var Authenticator *spotifyauth.Authenticator

func InitAuthenticator(cfg *config.Config) {
	Authenticator = spotifyauth.New(
		spotifyauth.WithRedirectURL(cfg.Url+"/callback"),
		spotifyauth.WithScopes(spotifyauth.ScopePlaylistReadPrivate, spotifyauth.ScopePlaylistModifyPrivate, spotifyauth.ScopeUserLibraryRead, spotifyauth.ScopePlaylistModifyPublic),
	)
}
