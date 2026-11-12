from fastapi import APIRouter, HTTPException
from sqlalchemy import text # wird nur fuer Test benoetigt
from session import db_dep
from models import Task
from sqlmodel import select


# router definieren / Erstellt und konfiguriert den Router für alle "/tasks"-Endpunkte
router = APIRouter(prefix="/tasks", tags=["tasks"])

# Test ohne Datenbankzugriff
@router.get("/test-router")
async def test_router():
    return {"message": "Unnoetig sein Vater"}

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

# Read: einzelne Aufgabe anhand ihrer ID abrufen
@router.get("/{task_id}", response_model=Task)
async def get_task(task_id: int, session: db_dep):
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# Update: Aufgabe aendern
@router.patch("/{task_id}", response_model=Task)
async def update_task(task_id: int, updated_task: Task, session: db_dep):
    # Vorhandene Aufgabe anhand ihrer ID suchen
    task = await session.get(Task, task_id)
    # Abbrechen, wenn die Aufgabe nicht existiert
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    # Neue Werte aus der PATCH-Request in die vorhandene Aufgabe ubernehmen
    task.title = updated_task.title
    task.priority = updated_task.priority
    task.completed = updated_task.completed
    # Aenderungen speichern
    session.add(task)
    await session.commit()
    # Aktuellen Datenbankstand laden und zurueckgeben
    await session.refresh(task)
    return task

# Delete: Aufgabe loeschen
@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: int, session: db_dep):
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await session.delete(task)
    await session.commit()
    return