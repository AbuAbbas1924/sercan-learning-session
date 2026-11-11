from sqlmodel import SQLModel, Field

class Aufgaben(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    priority: int
    completed: bool = False