from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel, Field
from contextlib import asynccontextmanager

# Beschreibt die Tabelle für unsere Aufgaben.
class Aufgabe(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    titel: str
    erledigt: bool = False

# Zugang zu unserer SQLite-Datenbank vorbereiten.
async_engine = create_async_engine(
    "sqlite+aiosqlite:///./todos.db",
    echo=True,
)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Beim Start: Verbindung öffnen und fehlende Tabellen erstellen.
    async with async_engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)

    # Währenddessen läuft unsere API.
    yield

    # Beim Beenden: Datenbankverbindungen freigeben.
    await async_engine.dispose()


app = FastAPI(lifespan=lifespan)

# Unsere lokale Oberfläche darf API-Antworten lesen.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ],
    allow_methods=["GET"],
)


@app.get("/")
async def start():
    return {"nachricht": "Unsere To-do-API läuft!"}