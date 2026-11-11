from contextlib import asynccontextmanager

from engine import init_db
from fastapi import FastAPI
from session import db_dep


print("---FastAPI started---") #Test

#Funktion mit lifespan
@asynccontextmanager
async def db_lifespan(app: FastAPI):
    print("DB starts")
    await init_db() 
    yield

app = FastAPI(lifespan=db_lifespan)

# Test beim Start
@app.get('/')
def test_start():
    return {"test": "Der Test hat funktioniert"} 

# Test fuer Session
@app.get('/test-session')
async def test_session(db: db_dep):
    return {"test": "Session wurde bereitgestellt"}


