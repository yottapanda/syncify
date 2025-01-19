import os

import spotipy
from flask import Flask, redirect, request, session

from dotenv import load_dotenv
from flask_session import Session

load_dotenv()

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY")

Session(app)

scope = "playlist-read-private,playlist-modify-private,user-library-read,playlist-modify-public"

@app.route("/auth/login")
def login():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    auth_url = auth_manager.get_authorize_url()

    return redirect(auth_url)

@app.route("/auth/callback")
def callback():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)

    session['token'] = auth_manager.get_access_token(request.args.get('code'))['access_token']

    return redirect('/')

@app.route("/logout")
def logout():
    session.clear()
    return redirect('/')

@app.route("/")
def home():
    if 'token' not in session:
        return f"""<html>
        <body>
            <h1>Syncify 2!</h1>
            <p>You are not currently logged in</p>
            <a href="/auth/login">Login</a>
        </body>
        </html>
        """
    spotify = spotipy.Spotify(auth=session['token'])
    user = spotify.current_user()
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
    return "Syncing... not implemented yet"
