from datetime import datetime

from sqlalchemy import select, exists
from sqlalchemy.orm import Session

from src.common import db, spotify


def run():
    with Session(db.engine) as db_session:
        stmt = select(db.User).where(
            ~exists(
                select(1)
                .select_from(db.SyncRequest)
                .where(
                    (db.SyncRequest.user_id == db.User.id)
                    & (db.SyncRequest.completed == None)
                )
            )
        )
        users = db_session.scalars(stmt).all()

        new_requests = []
        for user in users:
            client = spotify.get_client(user.id, db_session, commit=False)
            count = spotify.get_liked_count(client)
            new_requests.append(db.SyncRequest(user_id=user.id, song_count=count))

        db_session.add_all(new_requests)
        db_session.commit()

        print(f"Scheduled syncs for {len(users)} users at {datetime.now()}")
