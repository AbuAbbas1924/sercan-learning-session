from datetime import datetime  # Type for creation and modification timestamps.

from sqlalchemy import (  # func calls SQL functions; text defines SQL expressions.
    func,
    text,
)
from sqlmodel import (  # Field configures fields; SQLModel defines models.
    Field,
    SQLModel,
)


# database table
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True)
    password_hash: str
    created_at: datetime | None = Field(
        default=None, sa_column_kwargs={"server_default": text("now()")}
    )
    modified_at: datetime | None = Field(
        default=None,
        sa_column_kwargs={"server_default": text("now()"), "onupdate": func.now()},
    )

# registration input
class UserCreate(SQLModel):
    email: str
    password: str

# response data
class UserRead(SQLModel):
    id: int
    email: str
    created_at: datetime | None
