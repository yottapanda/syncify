import os
import secrets

import dotenv

dotenv.load_dotenv()

def _read(name: str, default: str = None, optional: bool = False) -> str:
    value = os.environ.get(name, default)
    if optional and not value:
        raise Exception("Environment variable {name} is not set")
    return value

db_file = _read("DB_FILE", default="./data/db.sqlite")
db_conn_string = f"sqlite:///{db_file}"

secret_key = _read("SECRET_KEY", secrets.token_hex())

production = _read("PRODUCTION", default="false").lower() in ('true', '1', 't')
