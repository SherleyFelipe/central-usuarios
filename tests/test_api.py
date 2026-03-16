import json
import os
import socket
import threading
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from uuid import uuid4

import uvicorn


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TMP_ROOT = PROJECT_ROOT / ".tmp_tests"
API_TOKEN = "test-token-123"


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class ApiIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        TMP_ROOT.mkdir(exist_ok=True)
        cls.db_path = TMP_ROOT / f"test_{uuid4().hex}.db"
        os.environ["API_USUARIOS_DB_PATH"] = str(cls.db_path)
        os.environ["API_USUARIOS_TOKEN"] = API_TOKEN

        from app.main import create_app

        cls.port = find_free_port()
        cls.server = uvicorn.Server(
            uvicorn.Config(
                create_app(),
                host="127.0.0.1",
                port=cls.port,
                log_level="warning",
            )
        )
        cls.thread = threading.Thread(target=cls.server.run, daemon=True)
        cls.thread.start()
        cls.wait_for_server()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.should_exit = True
        cls.thread.join(timeout=5)
        os.environ.pop("API_USUARIOS_DB_PATH", None)
        os.environ.pop("API_USUARIOS_TOKEN", None)
        if cls.db_path.exists():
            try:
                cls.db_path.unlink()
            except PermissionError:
                pass

    @classmethod
    def wait_for_server(cls) -> None:
        deadline = time.time() + 10
        while time.time() < deadline:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{cls.port}/health", timeout=1) as response:
                    if response.status == 200:
                        return
            except OSError:
                time.sleep(0.1)
        raise RuntimeError("API de teste nao iniciou a tempo")

    def request(
        self,
        method: str,
        path: str,
        payload: dict | None = None,
        token: str | None = None,
    ) -> tuple[int, dict]:
        data = None
        headers = {}
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        if token is not None:
            headers["X-API-Token"] = token

        request = urllib.request.Request(
            f"http://127.0.0.1:{self.port}{path}",
            data=data,
            headers=headers,
            method=method,
        )
        try:
            with urllib.request.urlopen(request, timeout=3) as response:
                body = response.read().decode("utf-8")
                return response.status, json.loads(body)
        except urllib.error.HTTPError as error:
            body = error.read().decode("utf-8")
            return error.code, json.loads(body)

    def test_crud_flow(self) -> None:
        status, created = self.request(
            "POST",
            "/usuarios",
            {"nome": "Maria Silva", "email": "maria@example.com"},
            token=API_TOKEN,
        )
        self.assertEqual(status, 201)
        self.assertEqual(created["nome"], "Maria Silva")

        status, listed = self.request("GET", "/usuarios")
        self.assertEqual(status, 200)
        self.assertGreaterEqual(len(listed), 1)

        user_id = created["id"]
        status, found = self.request("GET", f"/usuarios/{user_id}")
        self.assertEqual(status, 200)
        self.assertEqual(found["email"], "maria@example.com")

        status, updated = self.request(
            "PUT",
            f"/usuarios/{user_id}",
            {"nome": "Maria Souza", "email": "maria.souza@example.com"},
            token=API_TOKEN,
        )
        self.assertEqual(status, 200)
        self.assertEqual(updated["nome"], "Maria Souza")

        status, deleted = self.request("DELETE", f"/usuarios/{user_id}", token=API_TOKEN)
        self.assertEqual(status, 200)
        self.assertEqual(deleted["mensagem"], "Usuario removido com sucesso")

    def test_returns_404_for_missing_user(self) -> None:
        status, body = self.request("GET", "/usuarios/99999")
        self.assertEqual(status, 404)
        self.assertEqual(body["detail"], "Usuario nao encontrado")

    def test_rejects_duplicate_email(self) -> None:
        status, _ = self.request(
            "POST",
            "/usuarios",
            {"nome": "Joao", "email": "joao@example.com"},
            token=API_TOKEN,
        )
        self.assertEqual(status, 201)

        status, body = self.request(
            "POST",
            "/usuarios",
            {"nome": "Joao Clone", "email": "joao@example.com"},
            token=API_TOKEN,
        )
        self.assertEqual(status, 409)
        self.assertEqual(body["detail"], "Email ja cadastrado")

    def test_blocks_write_without_token(self) -> None:
        status, body = self.request(
            "POST",
            "/usuarios",
            {"nome": "Sem Token", "email": "sem-token@example.com"},
        )
        self.assertEqual(status, 401)
        self.assertEqual(body["detail"], "Token de acesso invalido")


if __name__ == "__main__":
    unittest.main()
