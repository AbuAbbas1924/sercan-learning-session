import asyncio

from fastapi import APIRouter
from models import User, UserCreate, UserRead
from security import hash_password
from session import db_dep

router = APIRouter(prefix="/auth", tags=["auth"])

# --- CRUD ---

# Create: Register a new user and store their hashed password.
@router.post("/register", response_model=UserRead, status_code=201)
async def register(data: UserCreate, session: db_dep):
    hashed_password = await asyncio.to_thread(
        hash_password, data.password
    )

    user = User(
        email=data.email,
        password_hash=hashed_password,
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user