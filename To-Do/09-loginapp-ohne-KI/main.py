import os
from contextlib import asynccontextmanager

from engine import async_engine, init_db
from fastapi import FastAPI
from session import db_dep
from sqlalchemy import text


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing database...")
    await init_db()
    yield
    await async_engine.dispose()

app = FastAPI(lifespan=lifespan)

@app.get('/')
def test():
    return {"test": "<=|-_-|=>"} 

# test db-connection
@app.get("/test-db")
async def test_db():
    try: 
        async with async_engine.connect() as connection:
            result = await connection.execute(text("SELECT 1"))
            return {"database_ok": result.scalar_one() == 1}
        
    except Exception as exc:
        print(exc) 
        return {"message": "Not connected"}

# test/check env variables
@app.get("/test-env")
def test_env():
    return {"env_test": os.getenv("ENV_TEST", "ENV_TEST is missing")}

# test session
@app.get("/test-session")
async def test_session(session: db_dep):
    result = await session.execute(text("SELECT 1"))
    return {"database_ok": result.scalar_one() == 1}