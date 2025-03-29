import os
import sqlite3


def connect():
    x = sqlite3.connect(
                os.environ["DB_FILE"],
                detect_types=sqlite3.PARSE_DECLTYPES
            )
    x.row_factory = sqlite3.Row
    return x
