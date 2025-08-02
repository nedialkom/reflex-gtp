import reflex as rx
import sqlalchemy
from datetime import datetime, timezone

from typing import List

from sqlmodel import Field, Relationship

def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ChatSession(rx.Model, table=True):
    messages : List['ChatSessionMessageModel'] = Relationship(back_populates='session')
    created_at: datetime = Field(
        default_factory=get_utc_now,
        sa_type=sqlalchemy.DateTime(timezone=True),
        sa_column_kwargs={
            "server_default": sqlalchemy.func.now()
        },
        nullable=False,
    )

    updated_at: datetime = Field(
        default_factory=get_utc_now,
        sa_type=sqlalchemy.DateTime(timezone=True),
        sa_column_kwargs={
            "onupdate":sqlalchemy.func.now(),
            "server_default": sqlalchemy.func.now()
        },
        nullable=False,
    )


class ChatSessionMessageModel(rx.Model, table=True):
    session_id: int = Field(default=None, foreign_key='chatsession.id')
    session:ChatSession = Relationship(back_populates='messages')
    content:str
    role: str
    created_at: datetime = Field(
        default_factory=get_utc_now,
        sa_type=sqlalchemy.DateTime(timezone=True),
        sa_column_kwargs={
            "server_default": sqlalchemy.func.now()
        },
        nullable=False,
    )



#class ChatMessageModel(rx.Model, table=True):
#    pass
