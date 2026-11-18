"""Einstiegspunkt: Erstellt die App und steuert ihren Lebenszyklus."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import async_engine, async_init_db
from .routes import router
from .seed import testbenutzer_erstellen

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

# FastAPI-Anwendung erstellen und Routen einbinden.
app = FastAPI(lifespan=lifespan)
app.include_router(router)
