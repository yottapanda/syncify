import uvicorn

from src import alembic
from src.common import conf
from src.webapp.app import app

if __name__ == '__main__':
    alembic.check()

    if conf.production:
        uvicorn.run(app, host='0.0.0.0', port=5000, workers=1)
    else:
        app.run(debug=True)
