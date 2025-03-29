import alembic.command
from alembic.config import Config


def check():
    alembic.command.check(Config("alembic.ini"))
