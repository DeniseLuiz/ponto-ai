from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.routes import router as auth_router
from app.companies.routes import router as companies_router
from app.employees.routes import router as employees_router
from app.jobs.routes import router as jobs_router

app = FastAPI(
    title="PontoAI — Extração Pericial de Ponto e Financeiro",
    description=(
        "API para extração automatizada de dados de cartões de ponto e "
        "fichas financeiras a partir de PDFs, utilizando Gemini 2.5 Pro."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # em produção, restrinja ao domínio do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(companies_router)
app.include_router(employees_router)
app.include_router(jobs_router)


@app.get("/health", tags=["Infra"])
def health_check():
    return {"status": "ok"}
