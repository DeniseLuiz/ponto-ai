from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr


# ==========================================
# 1. AUTENTICAÇÃO E SESSÃO
# ==========================================

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

TokenResponse = Token  # Suporta rotas antigas


class TokenData(BaseModel):
    user_id: int | None = None
    email: str | None = None


class LoginRequest(BaseModel):
    email: str | EmailStr
    username: str | None = None  # Suporta payloads antigos com username
    password: str


# ==========================================
# 2. USUÁRIO DO SISTEMA (USER)
# ==========================================

class UserBase(BaseModel):
    email: str
    full_name: str | None = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str
    company_id: int | None = None


class UserOut(UserBase):
    id: int
    company_id: int | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

UserResponse = UserOut  # Suporta rotas antigas


# ==========================================
# 3. EMPRESA (COMPANY)
# ==========================================

class CompanyBase(BaseModel):
    name: str
    cnpj: str | None = None
    active: bool = True


class CompanyCreate(CompanyBase):
    pass


class CompanyOut(CompanyBase):
    id: int
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

CompanyResponse = CompanyOut  # Suporta rotas antigas


# ==========================================
# 4. FUNCIONÁRIO (EMPLOYEE)
# ==========================================

class EmployeeBase(BaseModel):
    name: str
    cpf: str | None = None
    role_title: str | None = None
    username: str | None = None
    active: bool = True


class EmployeeCreate(EmployeeBase):
    password: str | None = None
    company_id: int


class EmployeeOut(EmployeeBase):
    id: int
    company_id: int
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

EmployeeResponse = EmployeeOut  # Suporta rotas antigas


# ==========================================
# 5. TAREFAS DE EXTRAÇÃO DE PONTO (JOB)
# ==========================================

class JobBase(BaseModel):
    role_mode: int
    employee_id: int | None = None


class JobCreate(JobBase):
    pass


class JobOut(JobBase):
    id: int
    user_id: int
    employee_id: int | None = None
    role_mode: int
    original_filename: str | None = None
    pdf_path: str | None = None
    result_path: str | None = None
    status: str
    error_message: str | None = None
    created_at: datetime | None = None
    finished_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

JobResponse = JobOut  # Suporta rotas antigas