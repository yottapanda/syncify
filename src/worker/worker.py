from datetime import datetime

import spotipy
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.common import db, spotify
from src.common.db import SyncRequest, User


def run():
    with Session(db.engine) as db_session:
        stmt = (
            select(SyncRequest)
            .join(User)
            .where(SyncRequest.completed == None)
            .order_by(SyncRequest.id.asc())
            .limit(1)
        )
        request = db_session.scalar(stmt)
        if not request:
            return

        access_token = spotify.get_access_token(request.user_id, db_session)
        if not access_token:
            print(f"Failed to get access token for user {request.user_id}")
            return

        client = spotipy.Spotify(auth=access_token)

        count = spotify.get_liked_count(client)
        if count is not request.song_count:
            request.song_count = count
            db_session.merge(request)
            db_session.commit()

        print(f"Starting {request.id} with {count} songs for {request.user_id}")
        for progress in spotify.sync(client):
            request.progress = progress / (
                count * 2
            )  # 1/2 for reading, 1/2 for writing
            db_session.merge(request)
            db_session.commit()

        request.completed = datetime.now()
        db_session.merge(request)
        db_session.commit()

        print(
            f"Sync {request.id} complete for {request.user_id}; {request.song_count} songs"
        )
