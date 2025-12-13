import uvicorn

from syncify2.common import alembic
from syncify2.common import conf
from syncify2.webapp.app import app

if __name__ == "__main__":
    alembic.check()

    uvicorn.run(app, host=conf.host, port=conf.port, workers=1)
