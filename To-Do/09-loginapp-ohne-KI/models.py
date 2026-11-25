from sqlmodel import Field, SQLModel


# database table
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True)
    password_hash: str

# registration input
class UserCreate(SQLModel):
    email: str
    password: str

# response data
class UserRead(SQLModel):
    id: int
    email: str