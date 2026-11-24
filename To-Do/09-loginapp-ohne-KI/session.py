from typing import Annotated

from engine import async_engine
from fastapi import Depends
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio.session import AsyncSession

# from collections.abc import AsyncIterator

# Session definieren
session_maker = async_sessionmaker(
    bind=async_engine, expire_on_commit=False, class_=AsyncSession
)

# KI sagt: async def get_session() -> AsyncIterator[AsyncSession]:
# Session initialisieren 
async def get_session() -> AsyncSession:
    async with session_maker() as session:
        yield session 

# Dependency
db_dep = Annotated[AsyncSession, Depends(get_session)]