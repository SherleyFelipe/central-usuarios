import sqlite3
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.auth import require_api_token
from app.database import get_connection, init_db
from app.schemas import Usuario, UsuarioEntrada


BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


def create_app() -> FastAPI:
    init_db()

    application = FastAPI(title="Central Usuarios API")
    application.mount("/app", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.get("/")
    def home() -> RedirectResponse:
        return RedirectResponse(url="/app/")

    @application.get("/health")
    def health() -> dict[str, str]:
        return {"mensagem": "API de usuarios funcionando"}

    @application.get("/usuarios")
    def listar_usuarios() -> list[Usuario]:
        with get_connection() as connection:
            rows = connection.execute(
                "SELECT id, nome, email FROM usuarios ORDER BY id"
            ).fetchall()
        return [Usuario(**dict(row)) for row in rows]

    @application.get("/usuarios/{usuario_id}")
    def buscar_usuario(usuario_id: int) -> Usuario:
        with get_connection() as connection:
            row = connection.execute(
                "SELECT id, nome, email FROM usuarios WHERE id = ?",
                (usuario_id,),
            ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Usuario nao encontrado")
        return Usuario(**dict(row))

    @application.post("/usuarios", status_code=201)
    def criar_usuario(dados: UsuarioEntrada, _: None = Depends(require_api_token)) -> Usuario:
        try:
            with get_connection() as connection:
                cursor = connection.execute(
                    "INSERT INTO usuarios (nome, email) VALUES (?, ?)",
                    (dados.nome, dados.email),
                )
                connection.commit()
                usuario_id = cursor.lastrowid
        except sqlite3.IntegrityError as error:
            if "UNIQUE constraint failed" in str(error):
                raise HTTPException(status_code=409, detail="Email ja cadastrado") from error
            raise
        return Usuario(id=usuario_id, **dados.model_dump())

    @application.put("/usuarios/{usuario_id}")
    def atualizar_usuario(
        usuario_id: int,
        dados: UsuarioEntrada,
        _: None = Depends(require_api_token),
    ) -> Usuario:
        try:
            with get_connection() as connection:
                cursor = connection.execute(
                    """
                    UPDATE usuarios
                    SET nome = ?, email = ?
                    WHERE id = ?
                    """,
                    (dados.nome, dados.email, usuario_id),
                )
                connection.commit()
        except sqlite3.IntegrityError as error:
            if "UNIQUE constraint failed" in str(error):
                raise HTTPException(status_code=409, detail="Email ja cadastrado") from error
            raise
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Usuario nao encontrado")
        return Usuario(id=usuario_id, **dados.model_dump())

    @application.delete("/usuarios/{usuario_id}")
    def remover_usuario(
        usuario_id: int,
        _: None = Depends(require_api_token),
    ) -> dict[str, str]:
        with get_connection() as connection:
            cursor = connection.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
            connection.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Usuario nao encontrado")
        return {"mensagem": "Usuario removido com sucesso"}

    return application


app = create_app()
