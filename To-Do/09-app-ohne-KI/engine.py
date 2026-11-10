from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel

async_engine = create_async_engine(
    "postgresql+asyncpg://postgres:postgres@todo-db:5432/sercan_todo",
    echo=True,
)

async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)