# Central Usuarios (FastAPI + Frontend)

Projeto simples de CRUD de usuarios com:
- Backend em FastAPI
- Frontend em HTML/CSS/JavaScript
- Persistencia em SQLite
- Autenticacao simples por token para operacoes de escrita

Links:
- App online: `https://central-usuarios.onrender.com/app/`
- Swagger: `https://central-usuarios.onrender.com/docs`
- GitHub: `https://github.com/SherleyFelipe/central-usuarios`

## 1. Requisitos

- Python 3.10+ instalado
- PowerShell (Windows)

## 2. Entrar na pasta do projeto

```powershell
cd "c:\Users\sherl\Documents\Portifolio\api-usuarios"
```

## 3. Criar e ativar ambiente virtual (primeira vez)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

## 4. Instalar dependencias (primeira vez)

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 5. Iniciar o projeto

Opcao rapida (recomendada):

```powershell
.\start_api.bat
```
Esse script abre uma nova janela do `cmd` com a API rodando.
Os dados ficam salvos em `data/usuarios.db`.
O token padrao para criar, editar e excluir e `portfolio-token-123`.

Opcao direta:

```powershell
.\venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

## 6. Abrir no navegador

- Frontend: `http://127.0.0.1:8000/app/`
- Swagger: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`

## 7. Testar CRUD no Swagger

No `http://127.0.0.1:8000/docs`:
- `POST /usuarios` cria
- `GET /usuarios` lista
- `GET /usuarios/{id}` busca
- `PUT /usuarios/{id}` atualiza
- `DELETE /usuarios/{id}` remove

Para `POST`, `PUT` e `DELETE`, envie o header:

```text
X-API-Token: portfolio-token-123
```

## 8. Rodar testes automatizados

```powershell
.\venv\Scripts\python.exe -m unittest tests.test_api
```

Os testes sobem a API localmente em uma porta livre e usam um banco SQLite temporario.
Tambem existe um workflow em [tests.yml](/c:/Users/sherl/Documents/Portifolio/api-usuarios/.github/workflows/tests.yml) para rodar esses testes no GitHub Actions a cada push e pull request.

## 9. Configuracao opcional

Variaveis de ambiente suportadas:
- `API_USUARIOS_DB_PATH`: caminho customizado do banco SQLite
- `API_USUARIOS_TOKEN`: token usado para operacoes de escrita

## 10. Rodar com Docker

Build da imagem:

```powershell
docker build -t central-usuarios .
```

Execucao do container:

```powershell
docker run -p 8000:8000 -e API_USUARIOS_TOKEN=portfolio-token-123 central-usuarios
```

Se quiser persistir os dados do SQLite com Docker, monte um volume para `/app/data`.

## 11. Deploy no Render

O projeto ja inclui [render.yaml](/c:/Users/sherl/Documents/Portifolio/api-usuarios/render.yaml) para deploy como Web Service no Render.

Passos:
1. Suba este projeto para um repositorio no GitHub.
2. No Render, crie um novo Blueprint ou Web Service apontando para esse repositorio.
3. Confirme os comandos:
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Defina o secret `API_USUARIOS_TOKEN`.
5. Aguarde o deploy terminar.

Links esperados apos deploy:
- Frontend: `https://SEU-SERVICO.onrender.com/app/`
- Swagger: `https://SEU-SERVICO.onrender.com/docs`
- Health: `https://SEU-SERVICO.onrender.com/health`

Observacao importante:
- o Render informa que Web Services precisam escutar em `0.0.0.0` e usar a porta fornecida por `PORT`
- sem disco persistente, o sistema de arquivos e efemero, entao o SQLite pode perder dados em restart ou redeploy
- se quiser persistencia no Render, adicione um disk com mount path `/opt/render/project/src/data`

## 12. Rodar com 1 clique no VS Code

Ja configurado neste projeto:
- `Terminal -> Run Task... -> Iniciar API FastAPI`
- ou `Run and Debug -> FastAPI (Uvicorn)` (F5), que inicia a API em `http://127.0.0.1:8001` e abre `http://127.0.0.1:8001/app/`

Observacao:
- `.\start_api.bat` e a execucao direta usam a porta `8000`
- o debug do VS Code (F5) usa a porta `8001` para evitar conflito quando a API ja estiver aberta na `8000`

## 13. Estrutura do projeto

- `app/auth.py`: validacao do token da API
- `app/main.py`: criacao da aplicacao e rotas
- `app/database.py`: inicializacao e conexao com SQLite
- `app/schemas.py`: modelos Pydantic
- `.github/workflows/tests.yml`: pipeline de testes no GitHub Actions
- `Dockerfile`: imagem para deploy em container
- `frontend/`: interface web
- `render.yaml`: configuracao de deploy no Render
- `tests/`: testes automatizados

## 14. Problemas comuns

- `Failed to fetch`: API nao esta rodando.
  - Solucao: executar `.\start_api.bat` e manter aberta a janela da API.
- erro de porta ao rodar no VS Code:
  - Solucao: usar o perfil `FastAPI (Uvicorn)` ja configurado na `8001`, ou fechar a instancia que estiver ocupando a `8000`.
- CSS/JS nao carregam:
  - Solucao: abrir `http://127.0.0.1:8000/app/` (nao abrir `index.html` direto).
- Pagina antiga:
  - Solucao: `Ctrl + F5`.
