# App 2 – Aufgabenboard

To-do-App mit Tailwind CSS, Alpine.js, FastAPI und SQLite.

## Funktionen

- Aufgaben hinzufügen und löschen
- Aufgaben als erledigt oder offen markieren
- Aufgaben durchsuchen
- Nach Alle, Offen und Erledigt filtern
- Aufgaben zählen
- Dauerhaft in SQLite speichern

## Starten

Im Ordner app-2 ausführen:

uv run uvicorn app_2.main:app --reload

Anschließend index.html über die VS-Code-Vorschau auf Port 3000 öffnen.
Der FastAPI-Server von App 1 muss vorher beendet sein.

## Datenbank

todos.db wird beim ersten Serverstart automatisch erstellt.