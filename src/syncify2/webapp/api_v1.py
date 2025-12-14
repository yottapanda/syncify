import secrets
from uuid import uuid4, UUID

from fastapi import Request, Depends, HTTPException, APIRouter
from fastapi_sessions.backends.session_backend import BackendError
from sqlalchemy import select
from starlette import status
from starlette.responses import Response, RedirectResponse

from syncify2.common import spotify, db
from syncify2.common.db import User, SyncRequest
from syncify2.webapp import session
from syncify2.webapp.session import SessionData
from syncify2.webapp.types import UserResponse

router = APIRouter(prefix="/api/v1", tags=["API v1"])


@router.get("/auth/login")
async def login(response: Response) -> str:
    session_id = uuid4()
    data = session.SessionData(state=secrets.token_urlsafe())
    await session.backend.create(session_id, data)
    session.cookie.attach_to_response(response, session_id)
    return spotify.oauth.get_authorize_url(data.state)


@router.get("/auth/callback", dependencies=[Depends(session.cookie)])
async def callback(
    request: Request,
    db_session: db.SessionDep,
    session_data: SessionData | BackendError = Depends(session.verifier),
    session_id: UUID = Depends(session.cookie),
):
    if request.query_params.get("state") != session_data.state:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Invalid state")
    token_response = spotify.oauth.get_access_token(request.query_params.get("code"))
    import spotipy

    client = spotipy.Spotify(auth=token_response["access_token"])
    user = client.current_user()
    db_session.merge(User(id=user["id"], refresh_token=token_response["refresh_token"]))
    db_session.commit()
    await session.backend.update(session_id, SessionData(user_id=user["id"]))
    return RedirectResponse("/dashboard", status_code=status.HTTP_302_FOUND)


@router.get("/auth/user", dependencies=[Depends(session.cookie)])
def get_user(
    db_session: db.SessionDep,
    session_data: SessionData | BackendError = Depends(session.verifier),
):
    if session_data.user_id is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not logged in")
    client = spotify.get_client(session_data.user_id, db_session)
    user = client.me()
    return UserResponse(id=user["id"], display_name=user["display_name"])


@router.get("/auth/logout", dependencies=[Depends(session.cookie)])
async def logout(session_id: UUID = Depends(session.cookie)):
    await session.backend.delete(session_id)


@router.put("/jobs", dependencies=[Depends(session.cookie)])
def enqueue(
    db_session: db.SessionDep,
    session_data: SessionData | BackendError = Depends(session.verifier),
):
    if session_data.user_id is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not logged in")
    stmt = select(SyncRequest).where(
        SyncRequest.user_id == session_data.user_id, SyncRequest.completed == None
    )
    if db_session.scalars(stmt).one_or_none():
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "You already have a pending sync request"
        )
    client = spotify.get_client(session_data.user_id, db_session)
    count = spotify.get_liked_count(client)
    sync_request = SyncRequest(user_id=session_data.user_id, song_count=count)
    db_session.add(sync_request)
    db_session.commit()


@router.get("/jobs", dependencies=[Depends(session.cookie)])
def jobs(
    db_session: db.SessionDep,
    session_data: SessionData | BackendError = Depends(session.verifier),
):
    if session_data.user_id is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not logged in")
    stmt = (
        select(SyncRequest)
        .where(SyncRequest.user_id == session_data.user_id)
        .order_by(SyncRequest.id.desc())
        .limit(10)
    )
    return db_session.scalars(stmt).all()


@router.delete("/jobs/{job_id}", dependencies=[Depends(session.cookie)])
def delete_job(
    job_id: int,
    db_session: db.SessionDep,
    session_data: SessionData | BackendError = Depends(session.verifier),
):
    if session_data.user_id is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not logged in")
    stmt = select(SyncRequest).where(
        SyncRequest.id == job_id,
        SyncRequest.user_id == session_data.user_id,
        SyncRequest.progress == 0,
    )
    job = db_session.scalars(stmt).one_or_none()
    if not job:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found")
    db_session.delete(job)
    db_session.commit()
