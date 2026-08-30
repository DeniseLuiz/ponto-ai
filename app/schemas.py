from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime

class CompanyBase(BaseModel):
    name: str
    cnpj: str
    active: bool = True

class CompanyCreate(CompanyBase):
    pass

class CompanyOut(CompanyBase):
    id: int
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True) # Para compatibilidade com Pydantic v2

class CompanyResponse(CompanyBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class EmployeeBase(BaseModel):
    name: str
    username: str
    active: bool = True

class EmployeeCreate(EmployeeBase):
    password: str
    company_id: UUID

class EmployeeResponse(EmployeeBase):
    id: UUID
    company_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"