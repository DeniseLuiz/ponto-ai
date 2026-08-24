from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas
from app.auth.security import get_current_user

router = APIRouter(prefix="/employees", tags=["Funcionários"])


@router.post("/", response_model=schemas.EmployeeOut, status_code=201)
def create_employee(
    payload: schemas.EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    company = db.query(models.Company).filter(models.Company.id == payload.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada.")

    employee = models.Employee(
        name=payload.name,
        cpf=payload.cpf,
        role_title=payload.role_title,
        company_id=payload.company_id,
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


@router.get("/", response_model=List[schemas.EmployeeOut])
def list_employees(
    company_id: int = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = db.query(models.Employee)
    if company_id:
        query = query.filter(models.Employee.company_id == company_id)
    return query.all()


@router.get("/{employee_id}", response_model=schemas.EmployeeOut)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado.")
    return employee


@router.delete("/{employee_id}", status_code=204)
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado.")
    db.delete(employee)
    db.commit()
