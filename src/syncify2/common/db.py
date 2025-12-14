from typing import Annotated, Any, Generator

from fastapi import Depends
from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    TIMESTAMP,
    create_engine,
    Float,
    func,
)
from sqlalchemy.orm import DeclarativeBase, mapped_column, Session

from syncify2.common import conf

engine = create_engine(conf.db_conn_string)


def get_session() -> Generator[Session, Any, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


class Base(DeclarativeBase):
    pass


class TimestampMixin(object):
    created = mapped_column(
        TIMESTAMP(True), nullable=False, server_default=func.now(), index=True
    )


class User(Base):
    __tablename__ = "users"

    id = mapped_column(String, primary_key=True)
    refresh_token = mapped_column(String, nullable=False)


class SyncRequest(Base, TimestampMixin):
    __tablename__ = "sync_requests"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id = mapped_column(String, ForeignKey("users.id"), nullable=False, index=True)
    song_count = mapped_column(Integer, nullable=False, default=0)
    progress = mapped_column(Float, nullable=False, default=0.0)
    completed = mapped_column(TIMESTAMP(True), nullable=True, index=True)
