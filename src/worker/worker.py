from datetime import datetime

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

        client = spotify.get_client(request.user_id, db_session)

        count = spotify.get_liked_count(client)
        if count != request.song_count:
            request.song_count = count
            db_session.merge(request)
            db_session.commit()

        print(f"Starting request {request.id} with {count} songs for {request.user_id}")
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
            f"Sync reqeust {request.id} complete for {request.user_id}; {request.song_count} songs"
        )
