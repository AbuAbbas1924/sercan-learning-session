"""Engine, Datenbank-Sessions und Erstellen der Tabellen."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from .config import database_url
from .models import Benutzer  # noqa: F401 - Registriert die Tabelle in SQLModel.metadata.

# Engine fÃ¼r den asynchronen Zugriff auf PostgreSQL erstellen.
async_engine = create_async_engine(
    database_url,
    echo=True,
    hide_parameters=True,
)

# FÃ¼r jede Anfrage, die diese Dependency verwendet,
# eine eigene Datenbank-Session bereitstellen.
async def get_session():
    async with AsyncSession(async_engine) as session:
        yield session
    # Nach der Verwendung wird die Session automatisch geschlossen.


# Steht SessionDependency in einer Route, ruft FastAPI get_session() auf
# und Ã¼bergibt der Route die dort bereitgestellte Datenbank-Session.
SessionDependency = Annotated[AsyncSession, Depends(get_session)]

# Die im Code beschriebenen Tabellen in der Datenbank erstellen.
async def async_init_db():
    async with async_engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)
