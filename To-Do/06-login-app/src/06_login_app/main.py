import os
from sqlalchemy import text
from pathlib import Path

from dotenv import load_dotenv

from typing import Annotated
from sqlmodel import Field, SQLModel, select
from fastapi import Depends, FastAPI, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from contextlib import asynccontextmanager
from pwdlib import PasswordHash


# Projektordner ermitteln:
# main.py → 06_login_app → src → 06-login-app
projektordner = Path(__file__).resolve().parents[2]

# Einstellungen aus der .env im Projektordner laden.
load_dotenv(projektordner / ".env")

# Die Datenbankadresse aus den Umgebungsvariablen auslesen.
database_url = os.getenv("DATABASE_URL")

# Ohne Datenbankadresse mit einer verständlichen Fehlermeldung abbrechen.
if not database_url:
    raise RuntimeError("DATABASE_URL fehlt. Prüfe deine .env-Datei.")


# Engine für den asynchronen Zugriff auf PostgreSQL erstellen.
async_engine = create_async_engine(
    database_url, 
    echo=True,
    hide_parameters=True,
)

# Für jede Anfrage, die diese Dependency verwendet,
# eine eigene Datenbank-Session bereitstellen.
async def get_session():
    async with AsyncSession(async_engine) as session:
        yield session
    # Nach der Verwendung wird die Session automatisch geschlossen.


# Wiederverwendbare Typangabe für unsere Endpoints.
SessionDependency = Annotated[AsyncSession, Depends(get_session)]

# Beschreibt die Datenbanktabelle für unsere Webseitenbenutzer.
class Benutzer(SQLModel, table=True):
    # Eindeutige ID, die beim Speichern automatisch vergeben wird.
    id: int | None = Field(default=None, primary_key=True)

    # Jeder Benutzername darf nur einmal vorkommen.
    benutzername: str = Field(unique=True, index=True)

    # Hier speichern wir später den Passwort-Hash.
    passwort_hash: str

# Welche Daten der Client bei der Anmeldung sendet.
class BenutzerLogin(SQLModel):
    benutzername: str = Field(min_length=1)
    passwort: str = Field(min_length=1)


# Welche Benutzerdaten die API zurückgeben darf.
class BenutzerAntwort(SQLModel):
    id: int
    benutzername: str

# Werkzeug zum Hashen und Prüfen von Passwörtern erstellen.
passwort_hasher = PasswordHash.recommended()


# Aus einem Klartextpasswort einen Hash erzeugen.
def passwort_hashen(passwort: str) -> str:
    return passwort_hasher.hash(passwort)


# Prüfen, ob das eingegebene Passwort zum gespeicherten Hash passt.
def passwort_pruefen(passwort: str, gespeicherter_hash: str) -> bool:
    return passwort_hasher.verify(passwort, gespeicherter_hash)

# Die im Code beschriebenen Tabellen in der Datenbank erstellen.
async def async_init_db():
    async with async_engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)
        await testbenutzer_erstellen()


async def testbenutzer_erstellen():
    # Zugangsdaten aus der .env auslesen.
    benutzername = os.getenv("TEST_BENUTZERNAME")
    passwort = os.getenv("TEST_PASSWORT")

    # Ohne Test-Zugangsdaten keinen Benutzer anlegen.
    if not benutzername or not passwort:
        return

    async with AsyncSession(async_engine) as session:
        # Prüfen, ob dieser Benutzer bereits existiert.
        abfrage = select(Benutzer).where(
            Benutzer.benutzername == benutzername
        )
        ergebnis = await session.exec(abfrage)
        vorhandener_benutzer = ergebnis.first()

        if vorhandener_benutzer is not None:
            return

        # Nur den Hash in der Datenbank speichern.
        neuer_benutzer = Benutzer(
            benutzername=benutzername,
            passwort_hash=passwort_hashen(passwort),
        )

        session.add(neuer_benutzer)
        await session.commit()

        print(">>> Testbenutzer wurde erstellt <<<")


# Steuert, was beim Starten und Beenden der Anwendung passiert.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Beim Start: fehlende Tabellen erstellen.
    await async_init_db()
    await testbenutzer_erstellen()
    print(">>> Datenbanktabellen sind bereit <<<")

    try:
        # Ab hier läuft die Anwendung und verarbeitet Anfragen.
        yield
    finally:
        # Beim Beenden: Verbindungspool der Engine schließen.
        await async_engine.dispose()

# FastAPI-Anwendung erstellen.
app = FastAPI(lifespan=lifespan)

@app.get("/")
async def start():
    return {"nachricht": "FastAPI läuft!"}

@app.get("/db-test")
async def datenbank_test(session: SessionDependency):
    # Die Abfrage jetzt über die bereitgestellte Session ausführen.
    ergebnis = await session.execute(text("SELECT 1"))

    wert = ergebnis.scalar_one()

    return {"datenbank": "verbunden", "ergebnis": wert}

@app.post("/login", response_model=BenutzerAntwort)
async def login(daten: BenutzerLogin, session: SessionDependency):
    # Benutzer anhand des eingegebenen Namens in PostgreSQL suchen.
    abfrage = select(Benutzer).where(Benutzer.benutzername == daten.benutzername)
    ergebnis = await session.exec(abfrage)
    benutzer = ergebnis.first()

    # Bei unbekanntem Benutzer oder falschem Passwort den Login ablehnen.
    if benutzer is None or not passwort_pruefen(daten.passwort, benutzer.passwort_hash):
        raise HTTPException(status_code=401, detail="Benutzername oder Passwort falsch")

    return benutzer