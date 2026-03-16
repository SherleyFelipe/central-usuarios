import os
import sqlite3
from pathlib import Path


DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "usuarios.db"


def get_database_path() -> Path:
    configured_path = os.getenv("API_USUARIOS_DB_PATH")
    if configured_path:
        return Path(configured_path)
    return DEFAULT_DB_PATH


def init_db(db_path: Path | None = None) -> Path:
    path = db_path or get_database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            )
            """
        )
        connection.commit()
    return path


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    path = init_db(db_path)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection
