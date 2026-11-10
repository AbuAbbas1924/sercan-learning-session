

from engine import init_db
from fastapi import FastAPI


app = FastAPI()
print("---FastAPI started---") #Test

#Funktion mit lifespan
await init_db()



# Test beim Start
@app.get('/')
def test():
    return {"test": "ok"} 


