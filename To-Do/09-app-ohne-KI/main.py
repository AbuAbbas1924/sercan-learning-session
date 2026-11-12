from contextlib import asynccontextmanager

from engine import init_db
from fastapi import FastAPI
from session import db_dep
from sqlalchemy import text # Fuer Test
from routing_tasks import router as tasks_router


print("---FastAPI started---") #Test

#Funktion mit lifespan
@asynccontextmanager
async def db_lifespan(app: FastAPI):
    print("DB starts")
    await init_db() 
    yield

app = FastAPI(lifespan=db_lifespan)
app.include_router(tasks_router) # router in main.py einbinden

@app.get("/test-db") # Sinvoller Test um Datenbankzugriff zu ueberpruefen
async def test_db(session: db_dep):
    result = await session.execute(text("SELECT 1"))
    return {"database_ok": result.scalar_one() == 1} 

