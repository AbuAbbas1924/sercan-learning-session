from engine import async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi import Depends
from typing import Annotated


# Session definieren
session_maker = async_sessionmaker(
    bind=async_engine, expire_on_commit=False, class_=AsyncSession
)

# Session initialisieren
async def get_session() -> AsyncSession:
    async with session_maker() as session:
        yield session

# Dependency
db_dep = Annotated[AsyncSession, Depends(get_session)]