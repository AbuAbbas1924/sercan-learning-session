from fastapi import APIRouter
from sqlalchemy import text # wird nur fuer Test benoetigt
from session import db_dep
from models import Task
from sqlmodel import select


# router definieren / Erstellt und konfiguriert den Router für alle "/tasks"-Endpunkte
router = APIRouter(prefix="/tasks", tags=["tasks"])

# Test ohne Datenbankzugriff
@router.get("/test-router")
async def test_router():
    return {"message": "Tasks-Router funktioniert"}

# Test mit Datenbankzugriff
@router.get("/test-router-db")
async def test_router_db(session: db_dep):
    result = await session.execute(text("SELECT 1"))
    return {"database_ok": result.scalar_one() == 1}

# --- CRUD ---

# Create: neue Aufgabe erstellen und speichern
@router.post("/", response_model=Task, status_code=201)
async def create_task(task: Task, session: db_dep):
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task

# Read: vorhandene Aufgaben abrufen
@router.get("/")
async def get_tasks(session: db_dep):
    tasks = await session.execute(select(Task))
    return tasks.scalars().all()
