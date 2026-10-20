
from contextlib import asynccontextmanager
from datetime import date
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import Field, SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession


# Unsere Datenbanktabelle.
class Aufgabe(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    titel: str
    status: str = Field(default="offen")
    prioritaet: str = Field(default="mittel")
    faellig_am: date | None = None


# Daten zum Erstellen einer Aufgabe.
class AufgabeErstellen(SQLModel):
    titel: str = Field(min_length=1)
    prioritaet: Literal["niedrig", "mittel", "hoch"] = "mittel"
    faellig_am: date | None = None


# Daten zum Bearbeiten einer Aufgabe.
# Alle Felder sind optional, damit nur ausgewählte Werte
# geändert werden können.
class AufgabeBearbeiten(SQLModel):
    titel: str | None = Field(default=None, min_length=1)
    status: Literal["offen", "in_arbeit", "erledigt"] | None = None
    prioritaet: Literal["niedrig", "mittel", "hoch"] | None = None
    faellig_am: date | None = None


# Eigene Datenbank für die erweiterte App 3.
async_engine = create_async_engine(
    "sqlite+aiosqlite:///./kanban_erweitert.db",
    echo=False,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)

    yield

    await async_engine.dispose()


app = FastAPI(lifespan=lifespan)


# Datenbank-Session für jeden Request.
async def get_session():
    async with AsyncSession(async_engine) as session:
        yield session


# Frontend darf auf unsere API zugreifen.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:3000",
        "http://localhost:3000",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
)


@app.get("/")
async def start():
    return {"nachricht": "Erweiterte Kanban-API läuft!"}


# GET: Alle Aufgaben lesen.
@app.get("/aufgaben")
async def aufgaben_lesen(
    session: Annotated[AsyncSession, Depends(get_session)],
):
    abfrage = select(Aufgabe).order_by(Aufgabe.id)
    ergebnis = await session.exec(abfrage)

    return ergebnis.all()


# POST: Neue Aufgabe erstellen.
@app.post("/aufgaben", status_code=201)
async def aufgabe_erstellen(
    daten: AufgabeErstellen,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    titel = daten.titel.strip()

    if not titel:
        raise HTTPException(
            status_code=422,
            detail="Titel darf nicht leer sein",
        )

    neue_aufgabe = Aufgabe(
        titel=titel,
        prioritaet=daten.prioritaet,
        faellig_am=daten.faellig_am,
    )

    session.add(neue_aufgabe)
    await session.commit()
    await session.refresh(neue_aufgabe)

    return neue_aufgabe


# PATCH: Aufgabe bearbeiten oder Status ändern.
@app.patch("/aufgaben/{aufgabe_id}")
async def aufgabe_bearbeiten(
    aufgabe_id: int,
    daten: AufgabeBearbeiten,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    aufgabe = await session.get(Aufgabe, aufgabe_id)

    if aufgabe is None:
        raise HTTPException(
            status_code=404,
            detail="Aufgabe nicht gefunden",
        )

    # Nur die tatsächlich übermittelten Felder übernehmen.
    aenderungen = daten.model_dump(exclude_unset=True)

    for feld in ("titel", "status", "prioritaet"):
        if feld in aenderungen and aenderungen[feld] is None:
            raise HTTPException(
                status_code=422,
                detail=f"{feld} darf nicht null sein",
            )

    if "titel" in aenderungen:
        aenderungen["titel"] = aenderungen["titel"].strip()

        if not aenderungen["titel"]:
            raise HTTPException(
                status_code=422,
                detail="Titel darf nicht leer sein",
            )

    for feld, wert in aenderungen.items():
        setattr(aufgabe, feld, wert)

    session.add(aufgabe)
    await session.commit()
    await session.refresh(aufgabe)

    return aufgabe


# DELETE: Aufgabe löschen.
@app.delete("/aufgaben/{aufgabe_id}")
async def aufgabe_loeschen(
    aufgabe_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    aufgabe = await session.get(Aufgabe, aufgabe_id)

    if aufgabe is None:
        raise HTTPException(
            status_code=404,
            detail="Aufgabe nicht gefunden",
        )

    await session.delete(aufgabe)
    await session.commit()

    return {"nachricht": "Aufgabe gelöscht."}
