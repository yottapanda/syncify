import os
import time

import spotipy
import uvicorn
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, g
from flask_session import Session

from common.db import connect
from common.spotify import gen_auth_manager

load_dotenv()

temp_conn = connect()
with temp_conn as temp_db:
    temp_db.executescript(open('schema.sql').read())
temp_conn.close()

app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.secret_key = os.environ["SECRET_KEY"]
Session(app)


def get_db():
    with app.app_context():
        if 'db' not in g:
            g.db = connect()
        return g.db


def get_auth_manager():
    with app.app_context():
        if 'auth_manager' not in g:
            g.auth_manager = gen_auth_manager(spotipy.cache_handler.FlaskSessionCacheHandler(session))
        return g.auth_manager


@app.route("/auth/login")
def login():
    return render_template("login.html", login_url=get_auth_manager().get_authorize_url())


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
        return redirect('/auth/login')

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
    return render_template("index.html")


@app.route('/enqueue')
def enqueue():
    if 'id' not in session:
        return redirect('/')
    with get_db() as db:
        user = db.execute("SELECT access_token, access_token_expiry FROM users WHERE id = ?", (session['id'],)).fetchone()
    if user is None or user['access_token_expiry'] < time.time() + 300:
        return redirect('/')

    with get_db() as db:
        db.execute("INSERT INTO sync_requests (user_id) VALUES (?)", (session['id'],))

    return "Done"

if __name__ == '__main__':
    if os.environ.get('FLASK_ENV') == 'development':
        app.run(debug=True)
    else:
        uvicorn.run(app, host='0.0.0.0', port=5000, workers=1)
