from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean, func
from sqlalchemy.orm import relationship
from app.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    cnpj = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    users = relationship("User", back_populates="company")
    employees = relationship("Employee", back_populates="company")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    company = relationship("Company", back_populates="users")
    jobs = relationship("Job", back_populates="user")


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    cpf = Column(String, nullable=True)
    role_title = Column(String, nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    company = relationship("Company", back_populates="employees")
    jobs = relationship("Job", back_populates="employee")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_mode = Column(Integer, nullable=False)  # 1, 2 ou 3
    original_filename = Column(String, nullable=True)
    pdf_key = Column(String, nullable=False)       # chave do PDF original no Redis
    result_key = Column(String, nullable=True)      # chave do Excel gerado no Redis
    status = Column(String, nullable=False, default="pending")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    finished_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="jobs")
    employee = relationship("Employee", back_populates="jobs")
