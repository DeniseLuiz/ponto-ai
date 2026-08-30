from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app.models import Employee, Company, User
from app.schemas import EmployeeCreate, EmployeeResponse

# router = APIRouter(prefix="/employees", tags=["Employees"])
router = APIRouter(tags=["Employees"])

@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(employee_in: EmployeeCreate, db: Session = Depends(get_db)):
    # Valida se a empresa informada existe
    company = db.query(Company).filter(Company.id == employee_in.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")

    # O vínculo é feito com um User já existente, localizado pelo email.
    # Employee não guarda credenciais próprias (email/senha vivem só em User).
    user = db.query(User).filter(User.email == employee_in.email).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Nenhum usuário encontrado com esse email. Cadastre o usuário primeiro em POST /api/auth/register",
        )

    existing_employee = db.query(Employee).filter(Employee.user_id == user.id).first()
    if existing_employee:
        raise HTTPException(status_code=400, detail="Este usuário já está vinculado a um funcionário")

    new_employee = Employee(
        name=employee_in.name,
        cpf=employee_in.cpf,
        role_title=employee_in.role_title,
        company_id=employee_in.company_id,
        user_id=user.id,
    )
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return new_employee

@router.get("/company/{company_id}", response_model=List[EmployeeResponse])
def list_employees_by_company(company_id: int, db: Session = Depends(get_db)):
    return db.query(Employee).filter(Employee.company_id == company_id).all()
