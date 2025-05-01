import secrets
from uuid import uuid4, UUID

import spotipy
from fastapi import Request, Depends, HTTPException, APIRouter
from fastapi_sessions.backends.session_backend import BackendError

from sqlalchemy import select
from starlette import status
from starlette.responses import Response, RedirectResponse

from src.common import db, spotify
from src.common.db import User, SyncRequest
from src.webapp import session
from src.webapp.session import SessionData
from src.webapp.types import UserResponse

router = APIRouter(prefix="/api/v1", tags=["API v1"])


@router.get("/auth/login")
async def login(response: Response, post_callback_redirect_url: str) -> str:
    session_id = uuid4()
    data = session.SessionData(
        state=secrets.token_urlsafe(),
        post_callback_redirect_url=post_callback_redirect_url,
    )
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
    client = spotipy.Spotify(auth=token_response["access_token"])
    user = client.current_user()
    db_session.merge(User(id=user["id"], refresh_token=token_response["refresh_token"]))
    db_session.commit()
    await session.backend.update(session_id, SessionData(user_id=user["id"]))
    return RedirectResponse(
        session_data.post_callback_redirect_url, status_code=status.HTTP_302_FOUND
    )


@router.get("/auth/user", dependencies=[Depends(session.cookie)])
def get_user(
    db_session: db.SessionDep,
    session_data: SessionData | BackendError = Depends(session.verifier),
):
    if session_data.user_id is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not logged in")
    access_token = spotify.get_access_token(session_data.user_id, db_session)
    client = spotipy.Spotify(auth=access_token)
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
    stmt = select(SyncRequest).where(
        SyncRequest.user_id == session_data.user_id, SyncRequest.completed == None
    )
    if db_session.scalars(stmt).one_or_none():
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "You already have a pending sync request"
        )
    db_session.add(SyncRequest(user_id=session_data.user_id))
    db_session.commit()


@router.get("/jobs", dependencies=[Depends(session.cookie)])
def jobs(
    db_session: db.SessionDep,
    session_data: SessionData | BackendError = Depends(session.verifier),
):
    stmt = (
        select(SyncRequest)
        .where(SyncRequest.user_id == session_data.user_id)
        .order_by(SyncRequest.id.asc())
        .limit(10)
    )
    return db_session.scalars(stmt).all()
