from pydantic import BaseModel, EmailStr, Field


class UsuarioEntrada(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100)
    email: EmailStr


class Usuario(UsuarioEntrada):
    id: int
