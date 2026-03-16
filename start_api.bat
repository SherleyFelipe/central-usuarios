@echo off
cd /d %~dp0
if not exist venv\Scripts\python.exe (
  echo [ERRO] Ambiente virtual nao encontrado em venv\Scripts\python.exe
  pause
  exit /b 1
)
start "Central Usuarios" cmd /k "cd /d %~dp0 && venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000"
