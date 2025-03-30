import spotipy
from spotipy import Spotify


def gen_auth_manager(cache_handler=None):
    scope = "playlist-read-private,playlist-modify-private,user-library-read,playlist-modify-public"
    return spotipy.oauth2.SpotifyOAuth(
        cache_handler=cache_handler,
        scope=scope)

def get_liked_track_uris(spotify: Spotify):
    results = spotify.current_user_saved_tracks(limit=50, offset=0)

    liked_track_uris = []

    for track in results['items']:
        liked_track_uris.append(track['track']['uri'])

    while results['next']:
        results = spotify.next(results)
        for track in results['items']:
            liked_track_uris.append(track['track']['uri'])

    return liked_track_uris


def get_playlist_id(spotify: Spotify, playlist_name):
    results = spotify.current_user_playlists(limit=50, offset=0)

    for playlist in results['items']:
        if playlist['name'] == playlist_name:
            return playlist['id']

    while results['next']:
        results = spotify.next(results)
        for playlist in results['items']:
            if playlist['name'] == playlist_name:
                return playlist['id']

    user = spotify.current_user()
    playlist = spotify.user_playlist_create(user['id'], playlist_name, public=False)
    return playlist['id']

def sync(spotify: Spotify):
    track_uris_raw = get_liked_track_uris(spotify)

    track_uris = [track_uris_raw[i:i + 10000] for i in range(0, len(track_uris_raw), 10000)]

    for playlist_num, playlist_chunk in enumerate(track_uris, start=1):
        playlist_id = get_playlist_id(spotify, "Syncify (Liked Songs) " + str(playlist_num) + "/" + str(len(track_uris)))
        spotify.playlist_replace_items(playlist_id, [])

        chunks = [playlist_chunk[i:i + 50] for i in range(0, len(playlist_chunk), 50)]

        for chunk in chunks:
            spotify.playlist_add_items(playlist_id, chunk)
