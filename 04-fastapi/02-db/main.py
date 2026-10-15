import datetime
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import Field, SQLModel

# ! definition

async_engine = create_async_engine("sqlite+aiosqlite:///./test.db", echo=True)


async def async_init_db():
    async with async_engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)


@asynccontextmanager
async def async_lifespan(app: FastAPI):
    await async_init_db()
    print(">>> Database initialized <<<")
    yield
    await async_engine.dispose()
    print(">>> Lifespan ended <<<")


class TodoDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str | None = None
    completed: bool = False
    priority: int = 1
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
    )


app = FastAPI(lifespan=async_lifespan)
