from fastapi import FastAPI

# Unsere API-Anwendung erstellen.
app = FastAPI()


# Auf GET-Anfragen an die Adresse "/" reagieren.
@app.get("/")
async def start():
    return {"nachricht": "Unsere To-do-API läuft!"}