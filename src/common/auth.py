from spotipy import SpotifyOAuth
from sqlalchemy import orm

from src.common import db
from src.common.db import User


def get_access_token(user_id: str, auth_manager: SpotifyOAuth) -> str | None:
    with orm.Session(db.engine) as conn:
        user = conn.get(User, user_id)
        if user is None:
            print(f"user {user_id} not found")
            return None
        response = auth_manager.refresh_access_token(user.refresh_token)
        if not response:
            print(f"failed to refresh for user {user_id}")
            return None
        user.refresh_token = response['refresh_token']
        conn.merge(user)
        conn.commit()
        return response.get('access_token')
