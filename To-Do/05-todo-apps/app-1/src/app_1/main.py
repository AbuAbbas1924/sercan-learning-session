from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Unsere lokale Oberfläche darf API-Antworten lesen.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ],
    allow_methods=["GET"],
)


@app.get("/")
async def start():
    return {"nachricht": "Unsere To-do-API läuft!"}