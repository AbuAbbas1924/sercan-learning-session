"""Legt bei Bedarf den Testbenutzer aus der .env an."""

import os

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from .auth import passwort_hashen
from .database import async_engine
from .models import Benutzer

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
