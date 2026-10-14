from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)




@app.get("/")
async def test():
    return ["Text 1", "Text 2", "Text 3"]

@app.post("/")
async def textEmpfangen(daten: dict):
    print(daten)
    return daten