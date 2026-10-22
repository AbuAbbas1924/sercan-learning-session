from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine
from contextlib import 

async_engine = create_async_engine(
    "sqlite+aiosqlite:///./test.db",
    echo=True,
)

async def async_init_db():
    async with async_engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)

app = FastAPI()

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
