"""Einstellungen aus der .env im Projektordner."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Projektordner ermitteln:
# main.py â†’ 06_login_app â†’ src â†’ 06-login-app
projektordner = Path(__file__).resolve().parents[2]

# Einstellungen aus der .env im Projektordner laden.
load_dotenv(projektordner / ".env")

# Die Datenbankadresse aus den Umgebungsvariablen auslesen.
database_url = os.getenv("DATABASE_URL")

# Ohne Datenbankadresse mit einer verstÃ¤ndlichen Fehlermeldung abbrechen.
if not database_url:
    raise RuntimeError("DATABASE_URL fehlt. PrÃ¼fe deine .env-Datei.")

# Mit diesem geheimen SchlÃ¼ssel signiert und Ã¼berprÃ¼ft der Server seine Tokens.
jwt_secret = os.getenv("JWT_SECRET")
print("--- KONTROLLE ---") 
print(f"JWT-Schlüssel gesetzt: {bool(jwt_secret)}")
print("-----------------")
if not jwt_secret:
    raise RuntimeError("JWT_SECRET fehlt. PrÃ¼fe deine .env-Datei.")

JWT_ALGORITHMUS = "HS256"
JWT_DAUER_MINUTEN = 30
