import spotipy

import flask_session
from flask import Flask, redirect, render_template, request, session, g

from sqlalchemy import orm, select

from src.common import conf, db
from src.common.auth import get_access_token
from src.common.db import User, SyncRequest
from src.common.spotify import gen_auth_manager

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = conf.secret_key
flask_session.Session(app)


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
    with orm.Session(db.engine) as conn:
        conn.merge(User(id=user['id'], refresh_token=token_response['refresh_token']))
        conn.commit()

    session['id'] = user['id']

    return redirect('/')


@app.route("/auth/logout")
def logout():
    session.clear()
    return redirect('/auth/login')


@app.route("/")
def home():
    if 'id' not in session:
        return redirect('/auth/login')

    access_token = get_access_token(session['id'], get_auth_manager())
    if not access_token:
        session.clear()
        return redirect('/auth/login')

    try:
        spotify = spotipy.Spotify(auth=access_token)
        user = spotify.current_user()
    except Exception as e:
        print(e)
        session.clear()
        return redirect('/auth/login')
    return render_template("index.html")


@app.route('/enqueue')
def enqueue():
    if 'id' not in session:
        return redirect('/auth/login')
    access_token = get_access_token(session['id'], get_auth_manager())
    if not access_token:
        session.clear()
        return redirect('/auth/login')
    try:
        spotify = spotipy.Spotify(auth=access_token)
        user = spotify.current_user()
    except Exception as e:
        print(e)
        session.clear()
        return redirect('/auth/login')

    with orm.Session(db.engine) as conn:
        conn.add(SyncRequest(user_id=user['id']))
        conn.commit()

    return "Done"

@app.route('/jobs', methods=['GET'])
def jobs():
    if 'id' not in session:
        return redirect('/auth/login')
    access_token = get_access_token(session['id'], get_auth_manager())
    if not access_token:
        session.clear()
        return redirect('/auth/login')
    try:
        spotify = spotipy.Spotify(auth=access_token)
        user = spotify.current_user()
    except Exception as e:
        print(e)
        session.clear()
        return redirect('/auth/login')

    with orm.Session(db.engine) as conn:
        js = conn.scalars(select(SyncRequest).where(SyncRequest.user_id.is_(user['id']))).all()

    for job in js:
        if not job.completed:
            job.status = "Pending"
        elif job.progress > 0:
            job.status = "Running"
        else:
            job.status = "Completed"

    return render_template("jobs.html", jobs=js)
