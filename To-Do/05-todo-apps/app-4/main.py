from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Field
from sqlalchemy.ext.asyncio import create_async_engine
from contextlib import asynccontextmanager



class Aufgabe(SQLModel):
    titel: str

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
async def aufgabe_empfangen(aufgabe: Aufgabe):
    return aufgabe
