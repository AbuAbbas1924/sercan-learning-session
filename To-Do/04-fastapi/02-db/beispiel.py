from typing import Optional
from fastapi import FastAPI, Depends
from sqlmodel import Field, SQLModel, Session, create_engine, select

# 1. SQLite Datenbank-Konfiguration
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# check_same_thread=False ist für SQLite in FastAPI zwingend erforderlich
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args, echo=True)


# 2. Datenmodell mit Auto-Increment ID
class Hero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    secret_name: str


# Datenbanktabellen beim Starten der App erstellen
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# 3. FastAPI App & DB-Session-Dependency
app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

def get_session():
    with Session(engine) as session:
        yield session


# 4. API Endpunkte
@app.post("/heroes/", response_model=Hero)
def create_hero(hero: Hero, session: Session = Depends(get_session)):
    session.add(hero)
    session.commit()       # Hier generiert SQLite die Auto-Increment ID
    session.refresh(hero)  # Holt die generierte ID zurück in das Objekt
    return hero

@app.get("/heroes/", response_model=list[Hero])
def read_heroes(session: Session = Depends(get_session)):
    heroes = session.exec(select(Hero)).all()
    return heroes
