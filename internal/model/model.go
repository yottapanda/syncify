package model

import (
	"github.com/yottapanda/syncify/internal/config"
	"github.com/zmb3/spotify/v2"
)

type Model struct {
	Plausible   *config.Plausible
	User        *spotify.PrivateUser
	SyncOutcome *SyncResponse
}

type SyncResponse struct {
	Count       int
	PlaylistUrl string
	Err         error
}
