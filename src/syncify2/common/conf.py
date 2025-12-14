import datetime
import os
import secrets

import dotenv
import posthog

dotenv.load_dotenv()


def _read(name: str, default: str = None, optional: bool = False) -> str:
    value = os.environ.get(name, default)
    if value == "":
        value = None
    if not optional and not value:
        raise Exception(f"Environment variable {name} is not set")
    return value


def _read_int(name: str, default: int = None, optional: bool = False) -> int:
    return int(_read(name, default=str(default), optional=optional))


def _read_bool(name: str, default: bool = False) -> bool:
    return _read(name, default=str(default), optional=True).lower() == "true"


host = _read("HOST", "0.0.0.0")
port = _read_int("PORT", 5000)

base_uri = _read("BASE_URI", "http://127.0.0.1:5000").removesuffix("/")

db_host = _read("DB_HOST", "localhost")
db_port = _read_int("DB_PORT", 5432)
db_name = _read("DB_NAME", "postgres")
db_user = _read("DB_USER", "postgres")
db_password = _read("DB_PASSWORD", "syncify")

db_conn_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

secret_key = _read("SECRET_KEY", default=secrets.token_hex())

scheduler_interval = datetime.timedelta(seconds=_read_int("SCHEDULER_INTERVAL", 86400))

# Set in docker image, mainly for development
website_path = _read("WEBSITE_PATH", default="frontend/dist", optional=True)

# Backend/server SDK configuration
posthog.host = _read("POSTHOG_HOST", default="https://eu.i.posthog.com", optional=True)
posthog.api_key = _read("POSTHOG_API_KEY", optional=True)
posthog.debug = _read_bool("POSTHOG_DEBUG", default="127.0.0.1" in base_uri)
