import os
import sqlite3
import time

import spotipy
from dotenv import load_dotenv
from flask import Flask, redirect, request, session, g
from flask_session import Session

load_dotenv()

app = Flask(__name__)

Session(app)

app.secret_key = os.environ["SECRET_KEY"]


def get_db():
    with app.app_context():
        if 'db' not in g:
            g.db = sqlite3.connect(
                os.environ["DB_FILE"],
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            g.db.row_factory = sqlite3.Row
        return g.db


def get_auth_manager():
    with app.app_context():
        scope = "playlist-read-private,playlist-modify-private,user-library-read,playlist-modify-public"
        if 'auth_manager' not in g:
            g.auth_manager = spotipy.oauth2.SpotifyOAuth(
                cache_handler=spotipy.cache_handler.FlaskSessionCacheHandler(session),
                scope=scope)
        return g.auth_manager


@app.route("/auth/login")
def login():
    return redirect(get_auth_manager().get_authorize_url())


@app.route("/auth/callback")
def callback():
    token_response = get_auth_manager().get_access_token(request.args.get('code'))
    spotify = spotipy.Spotify(auth=token_response['access_token'])
    user = spotify.current_user()
    with get_db() as db:
        db.execute(
            "INSERT OR REPLACE INTO users (id, access_token, access_token_expiry, refresh_token) VALUES (?, ?, ?, ?)",
            (
                user['id'],
                token_response['access_token'],
                token_response['expires_at'],
                token_response['refresh_token']
            )
        )

    session['id'] = user['id']

    return redirect('/')


@app.route("/logout")
def logout():
    session.clear()
    return redirect('/')


@app.route("/")
def home():
    if 'id' not in session:
        return f"""<html>
                <body>
                    <h1>Syncify 2!</h1>
                    <p>You are not currently logged in</p>
                    <a href="/auth/login">Login</a>
                </body>
                </html>
                """

    with get_db() as db:
        user = db.execute("SELECT access_token, access_token_expiry, refresh_token FROM users WHERE id = ?", (session['id'],)).fetchone()
        if user is None:
            session.clear()
            return "No user data"

        if user['access_token_expiry'] < time.time() + 300:
            refresh_response = None
            try:
                refresh_response = get_auth_manager().refresh_access_token(user['refresh_token'])
            except Exception as e:
                print(e)
            if refresh_response is None:
                db.execute("DELETE FROM users WHERE id = ?", session['id'])
                session.clear()
                return "Failed to refresh token"
            db.execute("UPDATE users SET access_token = ?, access_token_expiry = ?, refresh_token = ? WHERE id = ?", (
                refresh_response['access_token'],
                refresh_response['expires_at'],
                refresh_response['refresh_token'],
                session['id']
            ))
            token = refresh_response['access_token']
        else:
            token = user['access_token']

    try:
        spotify = spotipy.Spotify(auth=token)
        user = spotify.current_user()
    except Exception as e:
        print(e)
        session.clear()
        return redirect('/')
    return f"""<html>
    <body>
    <h1>Syncify 2!</h1>
    <p>Logged in as {user['display_name']}</p>
    <a href="/sync">Sync</a>
    <a href="/logout">Logout</a>
    </body>
    </html>"""


@app.route("/sync")
def sync():
    if 'id' not in session:
        return redirect('/')
    with get_db() as db:
        user = db.execute("SELECT access_token, access_token_expiry FROM users WHERE id = ?", (session['id'],)).fetchone()
    if user is None or user['access_token_expiry'] < time.time() + 300:
        return redirect('/')

    spotify = spotipy.Spotify(auth=user['access_token'])
    results = spotify.current_user_saved_tracks(limit=50, offset=0)

    track_ids = []

    for track in results['items']:
        track_ids.append(track['track']['id'])

    while results['next']:
        results = spotify.next(results)
        for track in results['items']:
            track_ids.append(track['track']['id'])
    
    return track_ids
