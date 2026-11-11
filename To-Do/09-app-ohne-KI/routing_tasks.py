from fastapi import APIRouter


# router definieren / Erstellt und konfiguriert den Router für alle "/tasks"-Endpunkte
router = APIRouter(prefix="/tasks", tags=["tasks"])

# Test ohne Datenbankzugriff
@router.get("/test-router")
async def test_router():
    return {"message": "Tasks-Router funktioniert"}


