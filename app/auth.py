import os

from fastapi import Header, HTTPException


DEFAULT_API_TOKEN = "portfolio-token-123"


def get_api_token() -> str:
    return os.getenv("API_USUARIOS_TOKEN", DEFAULT_API_TOKEN)


def require_api_token(x_api_token: str | None = Header(default=None)) -> None:
    if x_api_token != get_api_token():
        raise HTTPException(status_code=401, detail="Token de acesso invalido")
