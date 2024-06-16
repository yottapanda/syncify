package main

import (
	"errors"
	"github.com/sirupsen/logrus"
	"github.com/thechubbypanda/syncify/views"
	"github.com/zmb3/spotify/v2"
	spotifyauth "github.com/zmb3/spotify/v2/auth"
	"golang.org/x/oauth2"
	"net/http"
	"time"
)

func getLikedTrackIds(r *http.Request, s *spotify.Client) ([]spotify.ID, error) {
	var trackIds []spotify.ID

	tracks, err := s.CurrentUsersTracks(r.Context(), spotify.Limit(50))
	if err != nil {
		return nil, err
	}
	for _, t := range tracks.Tracks {
		trackIds = append(trackIds, t.SimpleTrack.ID)
	}

	for page := 1; ; page++ {
		err = s.NextPage(r.Context(), tracks)
		if errors.Is(err, spotify.ErrNoMorePages) {
			break
		}
		if err != nil {
			return nil, err
		}
		for _, t := range tracks.Tracks {
			trackIds = append(trackIds, t.SimpleTrack.ID)
		}
	}
	return trackIds, nil
}

func getPlaylist(r *http.Request, s *spotify.Client, user *spotify.PrivateUser) (*spotify.SimplePlaylist, error) {
	playlists, err := s.GetPlaylistsForUser(r.Context(), user.ID)
	if err != nil {
		return nil, err
	}
	logrus.Traceln(user.ID, ":", "reading page", 0, " of liked songs")
	for _, p := range playlists.Playlists {
		if p.Name == "Syncify" {
			return &p, nil
		}
	}

	for page := 1; ; page++ {
		err = s.NextPage(r.Context(), playlists)
		if errors.Is(err, spotify.ErrNoMorePages) {
			break
		}
		if err != nil {
			return nil, err
		}
		logrus.Traceln(user.ID, ":", "reading page", page, " of liked songs")
		for _, p := range playlists.Playlists {
			if p.Name == "Syncify" {
				return &p, nil
			}
		}
	}

	playlist, err := s.CreatePlaylistForUser(r.Context(), user.ID, "Syncify", "A copy of your 'Liked Songs' playlist by Syncify", false, false)
	if err != nil {
		return nil, err
	}

	logrus.Debugln(user.ID, ":", "created playlist", playlist.ID)

	return &playlist.SimplePlaylist, nil
}

func truncatePlaylist(r *http.Request, s *spotify.Client, user *spotify.PrivateUser, playlist *spotify.SimplePlaylist) error {
	var trackIds []spotify.ID

	// TODO (wasteful) https://github.com/zmb3/spotify/issues/262
	tracks, err := s.GetPlaylistItems(r.Context(), playlist.ID /*spotify.Fields("items(track(id))"),*/, spotify.Limit(50))
	if err != nil {
		return err
	}
	logrus.Traceln(user.ID, ":", "reading page", 0, " of tracks from playlist", playlist.ID)
	for _, t := range tracks.Items {
		trackIds = append(trackIds, t.Track.Track.ID)
	}

	for page := 1; ; page++ {
		err = s.NextPage(r.Context(), tracks)
		if errors.Is(err, spotify.ErrNoMorePages) {
			break
		}
		if err != nil {
			return err
		}
		logrus.Traceln(user.ID, ":", "reading page", page, " of tracks from playlist", playlist.ID)
		for _, t := range tracks.Items {
			trackIds = append(trackIds, t.Track.Track.ID)
		}
	}

	if len(trackIds) > 0 {
		for i := 0; i <= len(trackIds)/100; i++ {
			logrus.Traceln(user.ID, ":", "removing tracks", i*100, "-", min((i+1)*100, len(trackIds))-1, "from", playlist.ID)
			_, err := s.RemoveTracksFromPlaylist(r.Context(), playlist.ID, trackIds[i*100:min((i+1)*100, len(trackIds))]...)
			if err != nil {
				return err
			}
		}
	}

	return nil
}

func sync(r *http.Request, token *oauth2.Token) (int, error) {
	s := spotify.New(spotifyauth.New().Client(r.Context(), token))

	user, err := s.CurrentUser(r.Context())
	if err != nil {
		logrus.Errorln("failed to fetch user: ", err)
		return 0, err
	}

	logrus.Debugln(user.ID, ":", "starting sync")

	playlist, err := getPlaylist(r, s, user)
	if err != nil {
		logrus.Errorln(user.ID, ":", err)
		return 0, err
	}

	logrus.Debugln(user.ID, ":", "using playlist", playlist.ID)

	err = truncatePlaylist(r, s, user, playlist)
	if err != nil {
		logrus.Errorln(user.ID, ":", err)
		return 0, err
	}

	logrus.Debugln(user.ID, ":", "truncated playlist", playlist.ID)

	trackIds, err := getLikedTrackIds(r, s)
	if err != nil {
		logrus.Errorln(user.ID, ":", err)
		return 0, err
	}

	logrus.Debugln(user.ID, ":", "found", len(trackIds), "liked songs")

	if len(trackIds) > 0 {
		for i := 0; i <= len(trackIds)/100; i++ {
			logrus.Traceln(user.ID, ":", "adding tracks", i*100, "-", min((i+1)*100, len(trackIds))-1, "to", playlist.ID)
			_, err := s.AddTracksToPlaylist(r.Context(), playlist.ID, trackIds[i*100:min((i+1)*100, len(trackIds))]...)
			if err != nil {
				logrus.Errorln(user.ID, ":", err)
				return 0, err
			}
		}
	}

	logrus.Infoln(user.ID, ":", "sync complete for", len(trackIds), "songs")

	return len(trackIds), nil
}

func Sync(w http.ResponseWriter, r *http.Request) {
	token, ok := sm.Get(r.Context(), "token").(oauth2.Token)
	if !ok || token.Expiry.Before(time.Now()) {
		http.Redirect(w, r, "/login", http.StatusTemporaryRedirect)
		logrus.Traceln("no token or expired")
		return
	}

	count, err := sync(r, &token)
	err = views.Outcome(count, err).Render(w)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
}
