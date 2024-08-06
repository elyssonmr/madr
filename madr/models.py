from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, registry
from zoneinfo import ZoneInfo

table_registry = registry()


class BaseModel:
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False,
        server_default=func.now(),
        onupdate=datetime.now(tz=ZoneInfo('UTC')),
        nullable=False,
    )


@table_registry.mapped_as_dataclass
class User(BaseModel):
    __tablename__ = 'users'

    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)


@table_registry.mapped_as_dataclass
class Author(BaseModel):
    __tablename__ = 'authors'

    name: Mapped[str] = mapped_column(unique=True)
