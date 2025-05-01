import os
from pathlib import Path

from fastapi import FastAPI
from starlette import status
from starlette.responses import RedirectResponse, FileResponse
from starlette.staticfiles import StaticFiles

from src.common import conf
from src.webapp import api_v1

app = FastAPI()

app.include_router(api_v1.router)

if conf.website_path is not None:
    app.mount(
        "/static", StaticFiles(directory=conf.website_path, html=True), name="static"
    )

    # Catch-all route to serve index.html for any path not handled by API or static files
    @app.get("/{full_path:path}")
    async def spa(full_path: str):
        file_path = os.path.join(conf.website_path, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        else:
            return FileResponse(f"{conf.website_path}/index.html")
