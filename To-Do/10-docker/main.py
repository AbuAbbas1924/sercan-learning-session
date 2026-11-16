from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

app = FastAPI()

engine = create_async_engine(
    "postgresql+asyncpg://testpg:testpg@testpg-db:5432/semi"
)


@app.get("/test-db")
async def test_db():
    try: 
        async with engine.connect() as connection:
            result = await connection.execute(text("SELECT 1"))
            return {"database_ok": result.scalar_one() == 1}
        
    except: 
        return {"message": "Not connected"}

@app.get("/")
async def root():
    return {"message": "Ahlan wa sahlan"}