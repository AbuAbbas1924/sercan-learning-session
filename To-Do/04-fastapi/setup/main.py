from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

class TextDaten(BaseModel):
    text: str



@app.get("/")
async def test():
    return ["Text 1", "Text 2", "Text 3"]

@app.post("/")
async def textEmpfangen(daten: TextDaten):
    print(daten)
    return daten