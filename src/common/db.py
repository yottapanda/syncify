from datetime import datetime
from typing import Annotated, Any, Generator

from fastapi import Depends
from sqlalchemy import String, Integer, ForeignKey, TIMESTAMP, create_engine, Float
from sqlalchemy.orm import DeclarativeBase, mapped_column, Session

from src.common import conf, stripe

engine = create_engine(conf.db_conn_string)


def get_session() -> Generator[Session, Any, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = mapped_column(String, primary_key=True)
    refresh_token = mapped_column(String, nullable=False)
    stripe_customer_id = mapped_column(
        String, nullable=False, default=stripe.create_customer
    )


class SyncRequest(Base):
    __tablename__ = "sync_requests"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id = mapped_column(String, ForeignKey("users.id"), nullable=False, index=True)
    song_count = mapped_column(Integer, nullable=False, default=0)
    progress = mapped_column(Float, nullable=False, default=0.0)
    created = mapped_column(TIMESTAMP, nullable=False, default=datetime.now, index=True)
    completed = mapped_column(TIMESTAMP, nullable=True, index=True)
