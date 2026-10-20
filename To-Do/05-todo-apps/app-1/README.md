# To-do-App 1

Eine einfache Lern-App mit Tailwind CSS, Alpine.js, FastAPI und SQLite.

## Funktionen

- Aufgaben hinzufügen
- Gespeicherte Aufgaben anzeigen
- Aufgaben als erledigt oder offen markieren
- Aufgaben löschen

Die Aufgaben werden dauerhaft in der SQLite-Datei `todos.db` gespeichert.

## Voraussetzungen

- uv
- Python ab Version 3.14
- Internetverbindung für die eingebundenen Tailwind- und Alpine-Scripts

## Backend starten

Im Terminal in den Ordner `app-1` wechseln und ausführen:

```bash
uv sync
uv run uvicorn app_1.main:app --reload
```

Das Terminal geöffnet lassen.

- API: http://127.0.0.1:8000
- API-Testoberfläche: http://127.0.0.1:8000/docs

Die Datenbank und fehlende Tabellen werden beim Start automatisch angelegt.

## Frontend starten

Die `index.html` über die VS-Code-Vorschau auf Port 3000 öffnen.

Erlaubte Frontend-Ursprünge:

- http://127.0.0.1:3000
- http://localhost:3000

Das Backend muss gleichzeitig laufen.

## Projektdateien

- `index.html`: Oberfläche und Alpine.js-Funktionen
- `src/app_1/main.py`: API und Datenbankzugriff
- `pyproject.toml`: Projekteinstellungen und Abhängigkeiten
- `uv.lock`: Festgelegte Paketversionen
- `.gitignore`: Ausschluss lokaler Dateien aus Git

## Behobener Fehler

Der Server konnte zunächst wegen des fehlenden Pakets `greenlet`
nicht starten. Die Async-Abhängigkeiten wurden ergänzt mit:

```bash
uv add "sqlalchemy[asyncio]"
```

## Hinweise

- Den Backend-Server immer aus `app-1` starten, da der Datenbankpfad relativ ist.
- `todos.db` und `.venv` werden nicht mit Git gespeichert.
- Die App ist eine lokale Lernanwendung ohne Benutzeranmeldung.