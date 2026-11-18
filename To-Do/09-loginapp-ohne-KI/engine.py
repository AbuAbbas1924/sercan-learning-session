import models # Lets SQLModel discover the tables before create_all()
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel

async_engine = create_async_engine(
    "postgresql+asyncpg://postgres:postgres@my-postgres-container:5432/postgres-db",
    echo=True,
)

async def init_db():
    async with async_engine.begin() as conn: 
        await conn.run_sync(SQLModel.metadata.create_all) 