from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

app = FastAPI()

engine = create_async_engine(
    "postgresql+asyncpg://testpg:testpg@testpg-db:5432/semi"
)


@app.get("/test-db")
async def test_db():
    async with engine.connect() as connection:
        result = await connection.execute(text("SELECT 1"))
        return {"database_ok": result.scalar_one() == 1}

@app.get("/")
async def root():
    return {"message": "Ahlan wa sahlan"}