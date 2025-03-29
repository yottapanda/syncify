import spotipy


def gen_auth_manager(cache_handler=None):
    scope = "playlist-read-private,playlist-modify-private,user-library-read,playlist-modify-public"
    return spotipy.oauth2.SpotifyOAuth(
        cache_handler=cache_handler,
        scope=scope)

def get_liked_track_uris(spotify):
    results = spotify.current_user_saved_tracks(limit=50, offset=0)

    track_uris = []
    for track in results['items']:
        track_uris.append(track['track']['uri'])

    while results['next']:
        results = spotify.next(results)
        for track in results['items']:
            track_uris.append(track['track']['uri'])

    return track_uris


def get_playlist_id(spotify):
    results = spotify.current_user_playlists(limit=50, offset=0)

    for playlist in results['items']:
        if playlist['name'] == "Syncify (Liked Songs)":
            return playlist['id']

    while results['next']:
        results = spotify.next(results)
        for playlist in results['items']:
            if playlist['name'] == "Syncify (Liked Songs)":
                return playlist['id']

    user = spotify.current_user()
    playlist = spotify.user_playlist_create(user['id'], "Syncify (Liked Songs)", public=False)
    return playlist['id']

def sync(spotify):
    track_uris = get_liked_track_uris(spotify)
    playlist_id = get_playlist_id(spotify)

    spotify.playlist_replace_items(playlist_id, [])

    chunks = [track_uris[i:i + 50] for i in range(0, len(track_uris), 50)]

    for chunk in chunks:
        try:
            spotify.playlist_add_items(playlist_id, chunk)
        except Exception as e:
            # TODO Handle playlist sizing issue
            print(e)
