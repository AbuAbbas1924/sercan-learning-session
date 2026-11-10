import os
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from html import escape
from pathlib import Path
from typing import Annotated

import jwt
from dotenv import load_dotenv
from fastapi import Cookie, Depends, FastAPI, HTTPException, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from pwdlib import PasswordHash
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import Field, SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

# Projektordner ermitteln:
# main.py â†’ 06_login_app â†’ src â†’ 06-login-app
projektordner = Path(__file__).resolve().parents[2]

# Einstellungen aus der .env im Projektordner laden.
load_dotenv(projektordner / ".env")

# Die Datenbankadresse aus den Umgebungsvariablen auslesen.
database_url = os.getenv("DATABASE_URL")

# Ohne Datenbankadresse mit einer verstÃ¤ndlichen Fehlermeldung abbrechen.
if not database_url:
    raise RuntimeError("DATABASE_URL fehlt. PrÃ¼fe deine .env-Datei.")

# Mit diesem geheimen SchlÃ¼ssel signiert und Ã¼berprÃ¼ft der Server seine Tokens.
jwt_secret = os.getenv("JWT_SECRET")
print("--- KONTROLLE ---") 
print(f"JWT-Schlüssel gesetzt: {bool(jwt_secret)}")
print("-----------------")
if not jwt_secret:
    raise RuntimeError("JWT_SECRET fehlt. PrÃ¼fe deine .env-Datei.")

JWT_ALGORITHMUS = "HS256"
JWT_DAUER_MINUTEN = 30

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

# Beschreibt die Datenbanktabelle fÃ¼r unsere Webseitenbenutzer.
class Benutzer(SQLModel, table=True):
    # Eindeutige ID, die beim Speichern automatisch vergeben wird.
    id: int | None = Field(default=None, primary_key=True)

    # Jeder Benutzername darf nur einmal vorkommen.
    benutzername: str = Field(unique=True, index=True)

    # Hier speichern wir spÃ¤ter den Passwort-Hash.
    passwort_hash: str

# Welche Daten der Client bei der Anmeldung sendet.
class BenutzerLogin(SQLModel):
    benutzername: str = Field(min_length=1)
    passwort: str = Field(min_length=1)


# Welche Benutzerdaten die API zurÃ¼ckgeben darf.
class BenutzerAntwort(SQLModel):
    id: int
    benutzername: str

# Werkzeug zum Hashen und PrÃ¼fen von PasswÃ¶rtern erstellen.
passwort_hasher = PasswordHash.recommended()


# Aus einem Klartextpasswort einen Hash erzeugen.
def passwort_hashen(passwort: str) -> str:
    return passwort_hasher.hash(passwort)


# PrÃ¼fen, ob das eingegebene Passwort zum gespeicherten Hash passt.
def passwort_pruefen(passwort: str, gespeicherter_hash: str) -> bool:
    return passwort_hasher.verify(passwort, gespeicherter_hash)

def jwt_erstellen(benutzer_id: int) -> str:
    ablaufzeit = datetime.now(UTC) + timedelta(minutes=JWT_DAUER_MINUTEN)

   # sub enthÃ¤lt die Benutzer-ID. exp legt fest, bis wann der Token gÃ¼ltig ist.
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
        # Signatur und Ablaufzeit prÃ¼fen.
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
            detail="Anmeldung ungÃ¼ltig oder abgelaufen",
        )

    # Den Benutzer Ã¼ber seinen PrimÃ¤rschlÃ¼ssel aus PostgreSQL laden.
    benutzer = await session.get(Benutzer, benutzer_id)

    if benutzer is None:
        raise HTTPException(status_code=401, detail="Benutzer nicht gefunden")

    return benutzer


# Routen mit dieser Typangabe bekommen den Benutzer erst nach der JWT-PrÃ¼fung.
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
        # PrÃ¼fen, ob dieser Benutzer bereits existiert.
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
        # Ab hier lÃ¤uft die Anwendung und verarbeitet Anfragen.
        yield
    finally:
        # Beim Beenden: Verbindungspool der Engine schlieÃŸen.
        await async_engine.dispose()

# FastAPI-Anwendung erstellen.
app = FastAPI(lifespan=lifespan)

@app.get("/")
async def start():
    return {"nachricht": "FastAPI lÃ¤uft!"}

@app.get("/db-test")
async def datenbank_test(session: SessionDependency):
    # Die Abfrage jetzt Ã¼ber die bereitgestellte Session ausfÃ¼hren.
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

    # Der Browser speichert den Token und sendet ihn bei spÃ¤teren Anfragen mit.
    # HttpOnly verhindert, dass JavaScript den Cookie Ã¼ber document.cookie ausliest.
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,  # FÃ¼r den lokalen Test Ã¼ber HTTP. Bei HTTPS: True.
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
        # Dieselbe JWT-PrÃ¼fung verwenden wie bei /ich.
        benutzer = await get_current_user(session=session, access_token=access_token)
    except HTTPException as fehler:
        if fehler.status_code == 401:
            return RedirectResponse(url="/login", status_code=303)
        raise

    # escape wandelt z. B. < in &lt; um. So zeigt der Browser den Namen als Text an.
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
              <form method="post" action="/logout">
                <button type="submit">Abmelden</button>
              </form>
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
            // Wir senden die Felder selbst als JSON, wie POST /login sie erwartet.
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
                // Beim Aufruf des Dashboards sendet der Browser das Login-Cookie mit.
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

@app.post("/logout")
async def logout():
    # Nach dem POST soll der Browser die Login-Seite per GET Ã¶ffnen.
    antwort = RedirectResponse(url="/login", status_code=303)

    # Die Antwort weist den Browser an, das beim Login gesetzte Cookie zu lÃ¶schen.
    antwort.delete_cookie(key="access_token", path="/")

    return antwort