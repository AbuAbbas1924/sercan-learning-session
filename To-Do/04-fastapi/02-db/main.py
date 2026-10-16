from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel


async_engine = create_async_engine('sqlite+aiosqlite:///./test.db', echo=True)



async def async_init_db():
    async with async_engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)


@asynccontextmanager
async def async_lifespan(app: FastAPI):
    await async_init_db()
    print(">>> Database intialized <<<")
    yield
    await async_engine.dispose()
    print(">>> Lifespan ended <<<")
        


app = FastAPI(lifespan=async_lifespan)