from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app.models import Employee, Company
from app.schemas import EmployeeCreate, EmployeeResponse
from app.auth.security import get_password_hash

router = APIRouter(prefix="/employees", tags=["Employees"])

@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(employee_in: EmployeeCreate, db: Session = Depends(get_db)):
    # Valida se a empresa informada existe
    company = db.query(Company).filter(Company.id == employee_in.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")

    # Valida unicidade de username
    existing_user = db.query(Employee).filter(Employee.username == employee_in.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username já em uso")

    hashed_password = get_password_hash(employee_in.password)
    new_employee = Employee(
        name=employee_in.name,
        username=employee_in.username,
        password_hash=hashed_password,
        active=employee_in.active,
        company_id=employee_in.company_id
    )
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return new_employee

@router.get("/company/{company_id}", response_model=List[EmployeeResponse])
def list_employees_by_company(company_id: UUID, db: Session = Depends(get_db)):
    return db.query(Employee).filter(Employee.company_id == company_id).all()