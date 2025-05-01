import uvicorn

from src import alembic
from src.common import conf
from src.webapp.app import app

if __name__ == "__main__":
    alembic.check()

    uvicorn.run(app, host=conf.host, port=conf.port, workers=1)
