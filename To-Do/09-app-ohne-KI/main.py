from contextlib import asynccontextmanager

from engine import init_db
from fastapi import FastAPI


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
def test():
    return {"test": "ok"} 


