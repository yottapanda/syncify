import uvicorn

from common import conf, alembic
from webapp.app import app

if __name__ == "__main__":
    alembic.check()

    uvicorn.run(app, host=conf.host, port=conf.port, workers=1)
