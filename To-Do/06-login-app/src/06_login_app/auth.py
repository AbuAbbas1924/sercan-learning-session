"""Passwort-Hashes, JWTs und Ermitteln des angemeldeten Benutzers."""

from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Cookie, Depends, HTTPException
from pwdlib import PasswordHash

from .config import JWT_ALGORITHMUS, JWT_DAUER_MINUTEN, jwt_secret
from .database import SessionDependency
from .models import Benutzer

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
