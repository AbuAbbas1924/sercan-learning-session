"""Datenbankmodelle: table=True beschreibt eine Datenbanktabelle."""

from sqlmodel import Field, SQLModel

# Beschreibt die Datenbanktabelle fÃ¼r unsere Webseitenbenutzer.
class Benutzer(SQLModel, table=True):
    # Eindeutige ID, die beim Speichern automatisch vergeben wird.
    id: int | None = Field(default=None, primary_key=True)

    # Jeder Benutzername darf nur einmal vorkommen.
    benutzername: str = Field(unique=True, index=True)

    # Hier speichern wir spÃ¤ter den Passwort-Hash.
    passwort_hash: str
