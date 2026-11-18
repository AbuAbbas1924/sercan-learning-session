"""Ein- und Ausgabedaten der API, ohne eigene Datenbanktabellen."""

from sqlmodel import Field, SQLModel

# Welche Daten der Client bei der Anmeldung sendet.
class BenutzerLogin(SQLModel):
    benutzername: str = Field(min_length=1)
    passwort: str = Field(min_length=1)


# Welche Benutzerdaten die API zurÃ¼ckgeben darf.
class BenutzerAntwort(SQLModel):
    id: int
    benutzername: str
