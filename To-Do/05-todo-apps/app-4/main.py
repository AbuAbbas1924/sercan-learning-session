from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Field, select
from sqlalchemy.ext.asyncio import create_async_engine
from contextlib import asynccontextmanager
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Annotated




class Aufgabe(SQLModel):
    titel: str
class AufgabeStatus(SQLModel):
    completed: bool
class AufgabeDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    titel: str
    description: str | None = None
    completed: bool = False
    priority: int = 1

async_engine = create_async_engine(
    "sqlite+aiosqlite:///./mytodo.db",
    echo=True,
)


async def async_init_db():
    async with async_engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)

async def get_session():
    async with AsyncSession(async_engine) as session:
        yield session

SessionDependency = Annotated[AsyncSession, Depends(get_session)]
        

@asynccontextmanager
async def async_lifespan(app: FastAPI):
    await async_init_db()
    yield
    await async_engine.dispose()


app = FastAPI(lifespan=async_lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
async def test():
    return {'hello' : 'world'}

@app.post('/aufgaben')
async def aufgabe_empfangen(
    aufgabe: Aufgabe,
    session: SessionDependency,
    ):
    # getrimmt, weil strip() Leerzeichen am Anfang und am Ende entfernt
    getrimmter_titel = aufgabe.titel.strip() 
    if getrimmter_titel == "":
        raise HTTPException(
            status_code=422,
            detail="Der Titel darf nicht leer sein.",
        )
    neue_aufgabe = AufgabeDB(titel=getrimmter_titel)
    session.add(neue_aufgabe)
    await session.commit()
    await session.refresh(neue_aufgabe)
    return neue_aufgabe
    

@app.get('/aufgaben')
async def aufgaben_lesen(
    session: SessionDependency
):
    # abfrage = select(AufgabeDB)
    # ergebnis = await session.exec(abfrage)
    # return ergebnis.all()
    return ( await session.exec( select(AufgabeDB))).all()

@app.patch("/aufgaben/{aufgabe_id}")
async def aufgabe_status_aendern(
    aufgabe_id: int,
    daten: AufgabeStatus,
    session: SessionDependency,
):
    aufgabe = await session.get(AufgabeDB, aufgabe_id) 
    if aufgabe is None:
        raise HTTPException(
        status_code=404,
        detail="Aufgabe nicht gefunden",
        )
    aufgabe.completed = daten.completed
    await session.commit()
    await session.refresh(aufgabe)
    return aufgabe