import models
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel

async_engine = create_async_engine( # Erstellt asynchrone Engine fuer die Verbindung zur Datenbank
    "postgresql+asyncpg://postgres:postgres@todo-db:5432/sercan_todo", # Verbindungsadresse: Nutzer, Passwort, Host(Container-Name), Port und Datenbankname.
    echo=True, # SQL-Befehle werden im Terminal ausgegeben
)

async def init_db(): # asynchrone Funktion wird definiert => Soll Datenbanktabelle intialisieren
    async with async_engine.begin() as conn: # oeffnet eine Datenbankverbindung und startet eine Transaktion 
        await conn.run_sync(SQLModel.metadata.create_all) #Erstellt alle noch fehlenden Datenbanktabellen basierend auf den Modellen