import os

from fastapi import Header, HTTPException


def get_api_token() -> str | None:
    token = os.getenv("API_USUARIOS_TOKEN")
    if token is None:
        return None
    token = token.strip()
    return token or None


def require_api_token(x_api_token: str | None = Header(default=None)) -> None:
    configured_token = get_api_token()
    if configured_token is None:
        return
    if x_api_token != configured_token:
        raise HTTPException(status_code=401, detail="Token de acesso invalido")
