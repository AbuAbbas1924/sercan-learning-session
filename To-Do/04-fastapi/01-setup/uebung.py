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


# Erwartete Daten für den POST-Request
class TextDaten(BaseModel):
    text: str


# GET: Liste zurückgeben
@app.get("/")
async def liste_laden():
    return ["Get1", "Get2", "Get3", "Get4"]


# POST: Text entgegennehmen und zurückgeben
@app.post("/")
async def text_empfangen(daten: TextDaten):
    return daten