"""HTTP-Routen und HTML-Seiten der Login-App."""

from html import escape
from typing import Annotated

from fastapi import APIRouter, Cookie, HTTPException, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import text
from sqlmodel import select

from .auth import AngemeldeterBenutzer, get_current_user, jwt_erstellen, passwort_pruefen
from .config import JWT_DAUER_MINUTEN
from .database import SessionDependency
from .models import Benutzer
from .schemas import BenutzerAntwort, BenutzerLogin

router = APIRouter()

@router.get("/")
async def start():
    return {"nachricht": "FastAPI lÃ¤uft!"}

@router.get("/db-test")
async def datenbank_test(session: SessionDependency):
    # Die Abfrage jetzt Ã¼ber die bereitgestellte Session ausfÃ¼hren.
    ergebnis = await session.execute(text("SELECT 1"))

    wert = ergebnis.scalar_one()

    return {"datenbank": "verbunden", "ergebnis": wert}

@router.post("/login", response_model=BenutzerAntwort)
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

@router.get("/ich", response_model=BenutzerAntwort)
async def mein_profil(benutzer: AngemeldeterBenutzer):
    return benutzer

@router.get("/dashboard", response_class=HTMLResponse)
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

@router.get("/login", response_class=HTMLResponse)
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

@router.post("/logout")
async def logout():
    # Nach dem POST soll der Browser die Login-Seite per GET Ã¶ffnen.
    antwort = RedirectResponse(url="/login", status_code=303)

    # Die Antwort weist den Browser an, das beim Login gesetzte Cookie zu lÃ¶schen.
    antwort.delete_cookie(key="access_token", path="/")

    return antwort