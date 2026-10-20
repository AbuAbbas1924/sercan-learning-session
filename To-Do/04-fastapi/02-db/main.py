import datetime
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel, Field, select



async_engine = create_async_engine('sqlite+aiosqlite:///./test.db', echo=True, connect_args={"check_same_thread": False})



async def async_init_db():
    async with async_engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)


@asynccontextmanager
async def async_lifespan(app: FastAPI):
    await async_init_db()
    print(">>> Database intialized <<<")
    yield
    await async_engine.dispose()
    print(">>> Lifespan ended <<<")


class TodoDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str | None = None
    completed: bool = False
    priority: int = 1
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
        
async_session_setting = async_sessionmaker(async_engine, expire_on_commit=False)



async def async_get_session() -> AsyncSession:
    async with async_session_setting() as session:
        try:
            yield session
            print(">>> Yielding session <<<")
            await session.commit()
            print(">>> Commiting <<<")
        except Exception as e:
            print(f"an error occurred: {e}")
            await session.rollback()
            raise e
        finally:
            await session.close()
            print(">>> Closing session <<<")



async_session_dependency = Annotated[AsyncSession, Depends(async_get_session)]

app = FastAPI(lifespan=async_lifespan)

@app.post("/create", response_model=TodoDB)
async def create_todo(payload: TodoDB, session: async_session_dependency):
    todo = TodoDB.model_validate(payload)
    session.add(todo)
    await session.commit()
    await session.refresh(todo)
    return todo


@app.get("/all", response_model=list[TodoDB])
async def get_all(session: async_session_dependency):
    items = await session.execute(select(TodoDB))
    return items.scalars().all()