from fastapi import APIRouter
from sqlalchemy import text
from session import db_dep


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



