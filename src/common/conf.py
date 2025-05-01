import os
import secrets

import dotenv

dotenv.load_dotenv()


def _read(name: str, default: str = None, optional: bool = False) -> str:
    value = os.environ.get(name, default)
    if not optional and not value:
        raise Exception("Environment variable {name} is not set")
    return value


def _read_int(name: str, default: int = None, optional: bool = False) -> int:
    return int(_read(name, default=str(default), optional=optional))


def _read_bool(name: str, default: bool = False) -> bool:
    return _read(name, default=str(default), optional=True).lower() == "true"


host = _read("HOST", "localhost")
port = _read_int("PORT", 5000)

db_host = _read("DB_HOST", "localhost")
db_port = _read_int("DB_PORT", 5432)
db_name = _read("DB_NAME", "syncify2")
db_user = _read("DB_USER", "syncify2")
db_password = _read("DB_PASSWORD", "postgres")

db_conn_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

secret_key = _read("SECRET_KEY", secrets.token_hex())

website_path = _read("WEBSITE_PATH")
