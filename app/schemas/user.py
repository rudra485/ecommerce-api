from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True   # lets Pydantic read SQLAlchemy objects directly

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"