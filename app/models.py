from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean, func
from sqlalchemy.orm import relationship

from app.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    cnpj = Column(String, unique=True, nullable=True, index=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relacionamentos
    users = relationship("User", back_populates="company", cascade="all, delete-orphan")
    employees = relationship("Employee", back_populates="company", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relacionamentos
    company = relationship("Company", back_populates="users")
    jobs = relationship("Job", back_populates="user", cascade="all, delete-orphan")


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    cpf = Column(String, nullable=True, index=True)
    role_title = Column(String, nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relacionamentos
    company = relationship("Company", back_populates="employees")
    jobs = relationship("Job", back_populates="employee")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_mode = Column(Integer, nullable=False)  # Configuração de modo (1, 2 ou 3)
    original_filename = Column(String, nullable=True)
    pdf_path = Column(String, nullable=False)     # Mapeado também como pdf_key via código
    result_path = Column(String, nullable=True)   # Mapeado também como result_key via código
    status = Column(String, nullable=False, default="pending")  # pending, processing, done, failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    finished_at = Column(DateTime, nullable=True)

    # Relacionamentos
    user = relationship("User", back_populates="jobs")
    employee = relationship("Employee", back_populates="jobs")

    # Propriedades de conveniência para suportar chaves S3/MinIO
    @property
    def pdf_key(self):
        return self.pdf_path

    @pdf_key.setter
    def pdf_key(self, value):
        self.pdf_path = value

    @property
    def result_key(self):
        return self.result_path

    @result_key.setter
    def result_key(self, value):
        self.result_path = value