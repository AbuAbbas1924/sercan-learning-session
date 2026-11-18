# Login-App: Aufbau

Der Code liegt in `src/06_login_app/`:

| Datei | Aufgabe |
| --- | --- |
| `main.py` | Erstellt die FastAPI-App, startet die Datenbank und bindet die Routen ein. |
| `config.py` | Lädt die `.env` und stellt Datenbankadresse und JWT-Einstellungen bereit. |
| `database.py` | Erstellt die **Engine** (Verbindungspool), liefert pro Anfrage eine **Session** und erstellt die Tabellen. |
| `models.py` | Beschreibt mit `Benutzer` die Datenbanktabelle (`table=True`). |
| `schemas.py` | Beschreibt die Login-Eingabe und die erlaubte API-Antwort. Diese Klassen erzeugen keine Tabellen. |
| `auth.py` | Hasht und prüft Passwörter, erstellt JWTs und erkennt angemeldete Benutzer. |
| `seed.py` | Erstellt beim Start optional den Testbenutzer aus der `.env`. |
| `routes.py` | Enthält alle Endpunkte sowie die HTML-Seiten für Login und Dashboard. |

## Engine, Session und Model

Die **Engine** verwaltet die Verbindungen zur Datenbank. Eine **Session** verwendet diese Verbindungen, um Daten abzufragen oder zu speichern. Ein **Model** beschreibt dabei, wie eine Datenbanktabelle aufgebaut ist.

Beispiel: `POST /login` in `routes.py` bekommt über `SessionDependency` eine Session aus `database.py`. Die Route sucht damit einen `Benutzer` aus `models.py`. Die Funktionen aus `auth.py` prüfen das Passwort und erstellen den Token.

## Starten

Im Projektordner `06-login-app`:

```sh
uv run uvicorn 06_login_app.main:app --reload
```

Anschließend `http://127.0.0.1:8000/login` öffnen. Die vorhandene `.env` wird weiterhin aus dem Projektordner geladen. Benötigt werden `DATABASE_URL` und `JWT_SECRET`; `TEST_BENUTZERNAME` und `TEST_PASSWORT` sind optional.
