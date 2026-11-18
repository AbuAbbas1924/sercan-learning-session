from engine import async_engine
from fastapi import FastAPI
from sqlalchemy import text

app = FastAPI()

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