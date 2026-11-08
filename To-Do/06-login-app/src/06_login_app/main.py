import jwt
from datetime import datetime, timedelta, timezone
import os
from sqlalchemy import text
from pathlib import Path

from dotenv import load_dotenv

from html import escape
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Annotated
from sqlmodel import Field, SQLModel, select
from fastapi import Cookie, Depends, FastAPI, HTTPException, Response
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

jwt_secret = os.getenv("JWT_SECRET")
if not jwt_secret:
    raise RuntimeError("JWT_SECRET fehlt. Prüfe deine .env-Datei.")

JWT_ALGORITHMUS = "HS256"
JWT_DAUER_MINUTEN = 30

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

def jwt_erstellen(benutzer_id: int) -> str:
    ablaufzeit = datetime.now(timezone.utc) + timedelta(minutes=JWT_DAUER_MINUTEN)

    inhalt = {
        "sub": str(benutzer_id),
        "exp": ablaufzeit,
    }

    return jwt.encode(inhalt, jwt_secret, algorithm=JWT_ALGORITHMUS)

async def get_current_user(
    session: SessionDependency,
    access_token: Annotated[str | None, Cookie()] = None,
) -> Benutzer:
    # FastAPI liest das Cookie mit dem Namen "access_token".
    if not access_token:
        raise HTTPException(status_code=401, detail="Anmeldung erforderlich")

    try:
        # Signatur und Ablaufzeit prüfen.
        inhalt = jwt.decode(
            access_token,
            jwt_secret,
            algorithms=[JWT_ALGORITHMUS],
            options={"require": ["sub", "exp"]},
        )

        # Beim Erstellen des Tokens haben wir die ID als Text gespeichert.
        benutzer_id = int(inhalt["sub"])

    except (jwt.InvalidTokenError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Anmeldung ungültig oder abgelaufen",
        )

    # Den Benutzer über seinen Primärschlüssel aus PostgreSQL laden.
    benutzer = await session.get(Benutzer, benutzer_id)

    if benutzer is None:
        raise HTTPException(status_code=401, detail="Benutzer nicht gefunden")

    return benutzer


AngemeldeterBenutzer = Annotated[Benutzer, Depends(get_current_user)]

# Die im Code beschriebenen Tabellen in der Datenbank erstellen.
async def async_init_db():
    async with async_engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)


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
async def login(daten: BenutzerLogin, session: SessionDependency, response: Response):
    # Benutzer anhand des eingegebenen Namens in PostgreSQL suchen.
    abfrage = select(Benutzer).where(Benutzer.benutzername == daten.benutzername)
    ergebnis = await session.exec(abfrage)
    benutzer = ergebnis.first()

    # Bei unbekanntem Benutzer oder falschem Passwort den Login ablehnen.
    if benutzer is None or not passwort_pruefen(daten.passwort, benutzer.passwort_hash):
        raise HTTPException(status_code=401, detail="Benutzername oder Passwort falsch")

    token = jwt_erstellen(benutzer.id)

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,  # Für den lokalen Test über HTTP. Bei HTTPS: True.
        max_age=JWT_DAUER_MINUTEN * 60,
        path="/",
    )

    return benutzer

@app.get("/ich", response_model=BenutzerAntwort)
async def mein_profil(benutzer: AngemeldeterBenutzer):
    return benutzer

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    session: SessionDependency,
    access_token: Annotated[str | None, Cookie()] = None,
):
    try:
        # Dieselbe JWT-Prüfung verwenden wie bei /ich.
        benutzer = await get_current_user(session=session, access_token=access_token)
    except HTTPException as fehler:
        if fehler.status_code == 401:
            return RedirectResponse(url="/login", status_code=303)
        raise

    # Den Benutzernamen als Text in die HTML-Seite einsetzen.
    name = escape(benutzer.benutzername)

    return HTMLResponse(
        content=f"""
        <!doctype html>
        <html lang="de">
          <head>
            <meta charset="utf-8">
            <title>Dashboard</title>
          </head>
          <body>
            <main>
              <h1>Dashboard</h1>
              <p>Willkommen, {name}!</p>
            </main>
          </body>
        </html>
        """,
        headers={"Cache-Control": "no-store"},
    )

@app.get("/login", response_class=HTMLResponse)
async def login_seite():
    return """
    <!doctype html>
    <html lang="de">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Anmeldung</title>
      </head>
      <body>
        <main>
          <h1>Anmeldung</h1>

          <form id="login-formular" method="post" action="/login">
            <p>
              <label for="benutzername">Benutzername</label><br>
              <input id="benutzername" name="benutzername"
                     type="text" autocomplete="username" required>
            </p>

            <p>
              <label for="passwort">Passwort</label><br>
              <input id="passwort" name="passwort"
                     type="password" autocomplete="current-password" required>
            </p>

            <button type="submit">Anmelden</button>
            <p id="meldung" role="alert"></p>
          </form>
        </main>

        <script>
          const formular = document.getElementById("login-formular");
          const meldung = document.getElementById("meldung");

          formular.addEventListener("submit", async (event) => {
            event.preventDefault();
            meldung.textContent = "";

            const daten = {
              benutzername: document.getElementById("benutzername").value,
              passwort: document.getElementById("passwort").value
            };

            try {
              const antwort = await fetch("/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(daten)
              });

              if (antwort.ok) {
                window.location.assign("/dashboard");
              } else if (antwort.status === 401) {
                meldung.textContent = "Benutzername oder Passwort falsch.";
              } else {
                meldung.textContent = "Anmeldung fehlgeschlagen. Versuche es erneut.";
              }
            } catch {
              meldung.textContent = "Der Server ist gerade nicht erreichbar.";
            }
          });
        </script>
      </body>
    </html>
    """