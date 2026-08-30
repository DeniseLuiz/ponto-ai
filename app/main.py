import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.auth.routes import router as auth_router
from app.companies.routes import router as companies_router
from app.employees.routes import router as employees_router
from app.jobs.routes import router as jobs_router

# Resolução do caminho absoluto da pasta frontend na raiz do projeto
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

app = FastAPI(
    title="Ponto AI API",
    description="API de extração e análise inteligente de espelhos de ponto via IA",
    version="1.0.0"
)
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Permissão CORS para consumir via Front-end sem bloqueio no navegador
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusão dos roteadores de rotas da API
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(companies_router, prefix="/api/companies", tags=["Companies"])
app.include_router(employees_router, prefix="/api/employees", tags=["Employees"])
app.include_router(jobs_router, prefix="/api/jobs", tags=["Jobs"])

# Montagem de arquivos estáticos da interface web
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")