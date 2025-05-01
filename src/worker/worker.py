import threading
import time
from datetime import datetime

import spotipy
from sqlalchemy import asc, select
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
            .limit(10)
        )
        requests = db_session.scalars(stmt).all()

        for request in requests:
            access_token = spotify.get_access_token(request.user_id, db_session)
            if not access_token:
                print(f"Failed to get access token for user {request.user_id}")
                continue

            client = spotipy.Spotify(auth=access_token)
            print(f"Syncing for user {request.user_id}: {request.id}")
            spotify.sync(client)

            request.completed = datetime.now()
            db_session.merge(request)
            db_session.commit()

            print(f"Sync complete for user {request.user_id}: {request.id}")
