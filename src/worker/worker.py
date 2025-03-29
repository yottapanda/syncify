import threading
import time
from datetime import datetime

import spotipy
from sqlalchemy import asc
from sqlalchemy.orm import Session

from src.common import db
from src.common.auth import get_access_token
from src.common.db import SyncRequest, User
from src.common.spotify import gen_auth_manager, sync


class WorkerThread(threading.Thread):
    db = None

    def __init__(self):
        super().__init__()
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def _stopped(self) -> bool:
        return self.stop_event.is_set()

    def startup(self):
        pass

    def shutdown(self):
        pass

    def handle(self):
        with Session(db.engine) as conn:
            requests = conn.query(SyncRequest).filter(SyncRequest.completed == None).order_by(asc(SyncRequest.id)).limit(10).all()

        for request in requests:
            access_token = get_access_token(request.user.id, gen_auth_manager())
            if not access_token:
                print(f"Failed to get access token for user {request.user.id}")
                continue

            spotify = spotipy.Spotify(auth=access_token)
            print(f"Syncing for user {request.user.id}: {request.id}")
            sync(spotify)

            with Session(db.engine) as conn:
                request.completed = datetime.now()
                conn.merge(request)
                conn.commit()

            print(f"Sync complete for user {request.user.id}: {request.id}")

        if len(requests) == 0:
            time.sleep(1)

    def run(self):
        print("Worker startup")
        self.startup()
        while not self._stopped():
            self.handle()
        print("Worker graceful shutdown")
        self.shutdown()
