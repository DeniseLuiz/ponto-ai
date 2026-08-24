from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas
from app.auth.security import get_current_user

router = APIRouter(prefix="/companies", tags=["Empresas"])


@router.post("/", response_model=schemas.CompanyOut, status_code=201)
def create_company(
    payload: schemas.CompanyCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Cria uma nova empresa. Regra de negócio: 1 empresa pode ter N funcionários."""
    company = models.Company(name=payload.name, cnpj=payload.cnpj)
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.get("/", response_model=List[schemas.CompanyOut])
def list_companies(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.query(models.Company).all()


@router.get("/{company_id}", response_model=schemas.CompanyOut)
def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada.")
    return company


@router.delete("/{company_id}", status_code=204)
def delete_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada.")
    db.delete(company)
    db.commit()
