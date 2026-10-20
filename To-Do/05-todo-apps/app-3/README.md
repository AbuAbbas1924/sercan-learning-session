# App 3 – Kanban-Board

Kanban-App mit Tailwind CSS, Alpine.js, FastAPI und SQLite.

## Funktionen

- Aufgaben hinzufügen und löschen
- Aufgaben in drei Spalten verwalten: Offen, In Arbeit und Erledigt
- Aufgaben zwischen den Spalten verschieben
- Aufgaben durchsuchen
- Aufgaben pro Spalte zählen
- Dauerhaft in SQLite speichern

## Starten

Im Ordner `app-3` ausführen:

`uv run uvicorn app_3.main:app --reload`

Anschließend `index.html` über die VS-Code-Vorschau auf Port 3000 öffnen.

Der FastAPI-Server von App 2 muss vorher beendet sein.

## Datenbank

`kanban.db` wird beim ersten Serverstart automatisch erstellt.