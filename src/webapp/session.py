from uuid import UUID

from fastapi_sessions.backends.implementations import InMemoryBackend
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters
from pydantic import BaseModel

from src.common import conf


class SessionData(BaseModel):
    state: str | None = None
    user_id: str | None = None


cookie_params = CookieParameters()

# Uses UUID
cookie = SessionCookie(
    cookie_name="syncify_session",
    identifier="general_verifier",
    auto_error=True,
    secret_key=conf.secret_key,
    cookie_params=cookie_params,
)

from fastapi_sessions.session_verifier import SessionVerifier
from fastapi import HTTPException

backend = InMemoryBackend[UUID, SessionData]()


class Verifier(SessionVerifier[UUID, SessionData]):
    @property
    def identifier(self):
        return "general_verifier"

    @property
    def backend(self):
        return backend

    @property
    def auto_error(self):
        return True

    @property
    def auth_http_exception(self):
        return HTTPException(status_code=403, detail="invalid session")

    def verify_session(self, model: SessionData) -> bool:
        return True


verifier = Verifier()
