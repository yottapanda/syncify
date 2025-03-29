import os
import sqlite3
import threading
import time

import spotipy

from common.spotify import gen_auth_manager, sync

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
        self.db = sqlite3.connect(
            os.environ["DB_FILE"],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        self.db.row_factory = sqlite3.Row

    def shutdown(self):
        if self.db is not None:
            self.db.close()

    def handle(self):
        with self.db as conn:
            requests = conn.execute(
                "SELECT sync_requests.id as id, user_id, refresh_token FROM sync_requests JOIN users WHERE users.id = user_id AND done = 0 ORDER BY id LIMIT 10",
                ()).fetchall()
        for request in requests:
            auth_manager = gen_auth_manager()
            refresh_response = auth_manager.refresh_access_token(request['refresh_token'])

            with self.db as conn:
                conn.execute(
                    "UPDATE users SET access_token = ?, access_token_expiry = ?, refresh_token = ? WHERE id = ?", (
                        refresh_response['access_token'],
                        refresh_response['expires_at'],
                        refresh_response['refresh_token'],
                        request['user_id']
                    ))

            spotify = spotipy.Spotify(auth=refresh_response['access_token'])
            print("Syncing for user", request['user_id'], "id", request['id'])
            sync(spotify)

            with self.db as conn:
                conn.execute("UPDATE sync_requests SET done = 1 WHERE id = ?", (request['id'],))


            print("Sync complete for user", request['user_id'], "id", request['id'])
        if len(requests) == 0:
            time.sleep(1)

    def run(self):
        print("Worker startup")
        self.startup()
        while not self._stopped():
            self.handle()
        print("Worker graceful shutdown")
        self.shutdown()
