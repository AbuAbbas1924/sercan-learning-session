from sqlmodel import SQLModel, Field

# class Task(SQLModel, table=True):
#     id: int | None = Field(primary_key=True)
#     title: str | None
#     priority: int | None
#     completed: bool | None = False 

# Ki sagt so besser
class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    priority: int
    completed: bool = False
