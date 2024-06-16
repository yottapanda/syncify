package main

import (
	"errors"
	"github.com/sirupsen/logrus"
	"github.com/thechubbypanda/spotisync/views"
	"github.com/zmb3/spotify/v2"
	spotifyauth "github.com/zmb3/spotify/v2/auth"
	"golang.org/x/oauth2"
	"net/http"
	"time"
)

func getLikes(r *http.Request, s *spotify.Client) ([]spotify.SimpleTrack, error) {
	var allTracks []spotify.SimpleTrack

	tracks, err := s.CurrentUsersTracks(r.Context(), spotify.Limit(50))
	if err != nil {
		return nil, err
	}
	for _, t := range tracks.Tracks {
		allTracks = append(allTracks, t.SimpleTrack)
	}

	for page := 1; ; page++ {
		logrus.Trace("Fetching page", page)
		err = s.NextPage(r.Context(), tracks)
		if errors.Is(err, spotify.ErrNoMorePages) {
			break
		}
		if err != nil {
			return nil, err
		}
		for _, t := range tracks.Tracks {
			allTracks = append(allTracks, t.SimpleTrack)
		}
	}
	return allTracks, nil
}

func Sync(w http.ResponseWriter, r *http.Request) {
	token, ok := sm.Get(r.Context(), "token").(oauth2.Token)
	if !ok || token.Expiry.Before(time.Now()) {
		http.Redirect(w, r, "/login", http.StatusTemporaryRedirect)
		logrus.Traceln("no token or expired")
		return
	}
	s := spotify.New(spotifyauth.New().Client(r.Context(), &token))

	user, err := s.CurrentUser(r.Context())
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		logrus.Errorln(err)
		return
	}

	playlist, err := s.CreatePlaylistForUser(r.Context(), user.ID, "SpotiSync", "A copy of your 'Liked Songs' by SpotiSync ("+time.Now().Format(time.RFC3339)+")", true, false)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		logrus.Errorln(err)
		return
	}

	logrus.Debugln("Using playlist", playlist.Name, "("+playlist.ID+")")

	tracks, err := getLikes(r, s)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		logrus.Errorln(err)
		return
	}

	var trackIds []spotify.ID
	for _, t := range tracks {
		trackIds = append(trackIds, t.ID)
	}

	logrus.Debugln("Track count: ", len(trackIds))

	for i := 0; i <= len(trackIds)/100; i++ {
		logrus.Debugln("Adding", i*100, "to", min((i+1)*100, len(trackIds))-1)
		_, err := s.AddTracksToPlaylist(r.Context(), playlist.ID, trackIds[i*100:min((i+1)*100, len(trackIds))]...)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			logrus.Errorln(err)
			return
		}
	}

	err = views.Outcome(len(trackIds), nil).Render(w)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
}
