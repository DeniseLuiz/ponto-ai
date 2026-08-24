from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


# ---------- AUTH ----------
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    company_id: Optional[int] = None


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]
    company_id: Optional[int]

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ---------- COMPANY ----------
class CompanyCreate(BaseModel):
    name: str
    cnpj: Optional[str] = None


class CompanyOut(BaseModel):
    id: int
    name: str
    cnpj: Optional[str]

    class Config:
        from_attributes = True


# ---------- EMPLOYEE ----------
class EmployeeCreate(BaseModel):
    name: str
    cpf: Optional[str] = None
    role_title: Optional[str] = None
    company_id: int


class EmployeeOut(BaseModel):
    id: int
    name: str
    cpf: Optional[str]
    role_title: Optional[str]
    company_id: int

    class Config:
        from_attributes = True


# ---------- JOB ----------
class JobOut(BaseModel):
    id: int
    status: str
    role_mode: int
    original_filename: Optional[str]
    result_path: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    finished_at: Optional[datetime]

    class Config:
        from_attributes = True
