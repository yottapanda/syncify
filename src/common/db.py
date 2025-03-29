from datetime import datetime

from sqlalchemy import String, Integer, ForeignKey, TIMESTAMP, create_engine
from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship

from src.common import conf

engine = create_engine(conf.db_conn_string, echo=not conf.production)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id = mapped_column(String, primary_key=True)
    refresh_token = mapped_column(String, nullable=False)

class SyncRequest(Base):
    __tablename__ = 'sync_requests'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id = mapped_column(String, ForeignKey('users.id'), index=True)
    user = relationship("User", lazy='joined')
    song_count = mapped_column(Integer, nullable=False, default=0)
    progress = mapped_column(Integer, nullable=False, default=0)
    created = mapped_column(TIMESTAMP, nullable=False, default=datetime.now(), index=True)
    completed = mapped_column(TIMESTAMP, nullable=True, index=True)
