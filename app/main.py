from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.auth.routes import router as auth_router
from app.companies.routes import router as companies_router
from app.employees.routes import router as employees_router
from app.jobs.routes import router as jobs_router

app = FastAPI(title="Ponto AI API")

# Permissão CORS para consumir via Front-end sem bloqueio no navegador
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(companies_router, prefix="/api/companies", tags=["Companies"])
app.include_router(employees_router, prefix="/api/employees", tags=["Employees"])
app.include_router(jobs_router, prefix="/api/jobs", tags=["Jobs"])

# Montagem de arquivos estáticos
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")