from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel, Field, select
from sqlmodel.ext.asyncio.session import AsyncSession


# Beschreibt die Tabelle für unsere Aufgaben.
class Aufgabe(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    titel: str
    erledigt: bool = False

# Beschreibt die Daten, die beim Erstellen gesendet werden.
class AufgabeErstellen(SQLModel):
    titel: str = Field(min_length=1)

# Eingabedaten zum Ändern des Erledigt-Status.
class AufgabeStatus(SQLModel):
    erledigt: bool


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


# Stellt für eine Anfrage eine eigene Datenbank-Session bereit.
async def get_session():
    async with AsyncSession(async_engine) as session:
        yield session


# Unsere lokale Oberfläche darf API-Antworten lesen.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ],
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
)


# Test-Endpoint: Prüfen, ob unsere API läuft.
@app.get("/")
async def start():
    return {"nachricht": "Unsere To-do-API läuft!"}


# Alle Aufgaben aus der Datenbank abrufen.
@app.get("/aufgaben")
async def aufgaben_lesen(session: AsyncSession = Depends(get_session)):
    # Alle Aufgaben abfragen, nach ID sortiert.
    abfrage = select(Aufgabe).order_by(Aufgabe.id)

    # Die Abfrage über unsere Session ausführen.
    ergebnis = await session.exec(abfrage)

    # Alle gefundenen Aufgaben zurückgeben.
    return ergebnis.all()

@app.post("/aufgaben", status_code=201)
async def aufgabe_erstellen(
    daten: AufgabeErstellen,
    session: AsyncSession = Depends(get_session),
):
    # Aus den empfangenen Daten eine neue Aufgabe erstellen.
    neue_aufgabe = Aufgabe(titel=daten.titel)

    # Die Aufgabe für das Speichern vormerken.
    session.add(neue_aufgabe)

    # Die Änderung dauerhaft in der Datenbank speichern.
    await session.commit()

    # Die von SQLite vergebene ID und die gespeicherten Werte laden.
    await session.refresh(neue_aufgabe)

    return neue_aufgabe

@app.patch("/aufgaben/{aufgabe_id}")
async def aufgabe_status_aendern(
    aufgabe_id: int,
    daten: AufgabeStatus,
    session: AsyncSession = Depends(get_session),
):
    # Die Aufgabe anhand ihrer ID suchen.
    aufgabe = await session.get(Aufgabe, aufgabe_id)

    if aufgabe is None:
        raise HTTPException(
            status_code=404,
            detail="Aufgabe nicht gefunden",
        )

    # Den übermittelten Status übernehmen und speichern.
    aufgabe.erledigt = daten.erledigt
    await session.commit()
    await session.refresh(aufgabe)

    return aufgabe

@app.delete("/aufgaben/{aufgabe_id}")
async def aufgabe_loeschen(
    aufgabe_id: int,
    session: AsyncSession = Depends(get_session),
):
    # Die Aufgabe anhand ihrer ID suchen.
    aufgabe = await session.get(Aufgabe, aufgabe_id)

    if aufgabe is None:
        raise HTTPException(
            status_code=404,
            detail="Aufgabe nicht gefunden",
        )

    # Die Aufgabe zum Löschen vormerken.
    await session.delete(aufgabe)

    # Die Löschung dauerhaft speichern.
    await session.commit()

    return {"nachricht": "Aufgabe gelöscht."}