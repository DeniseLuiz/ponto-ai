from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Employee, Company
from app.schemas import LoginRequest, TokenResponse
from app.auth.security import verify_password, create_access_token
from app.redis import save_user_session

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    # 1. Busca o funcionário pelo username
    employee = db.query(Employee).filter(Employee.username == payload.username).first()
    if not employee or not verify_password(payload.password, employee.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha inválidos"
        )

    # 2. Bloqueia acesso caso o funcionário esteja inativo
    if not employee.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: Funcionário inativo"
        )

    # 3. Busca e valida status da empresa
    company = db.query(Company).filter(Company.id == employee.company_id).first()
    if not company or not company.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: Empresa inativa ou não encontrada"
        )

    # 4. Gera o Token e um novo session_id único
    token, session_id = create_access_token(
        data={"sub": str(employee.id), "company_id": str(company.id)}
    )

    # 5. Sobrescreve a sessão ativa no Redis (Derruba qualquer outro login ativo deste usuário)
    save_user_session(employee_id=str(employee.id), session_id=session_id)

    return TokenResponse(access_token=token)