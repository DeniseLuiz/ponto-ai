from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Company
from app.schemas import LoginRequest, TokenResponse, UserCreate, UserOut, RoleUpdate
from app.auth.security import verify_password, create_access_token, get_password_hash, require_admin
from app.redis import save_user_session

router = APIRouter(tags=["Auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email já em uso")

    # Bootstrap: o 1º usuário do sistema vira admin automaticamente
    # (resolve o problema de "quem cria o 1º admin, se criar empresa exige login").
    # Todos os demais entram como "user" por padrão — promoção é feita via
    # PATCH /api/auth/users/{user_id}/role, só por quem já é admin.
    role = "admin" if db.query(User).count() == 0 else "user"

    new_user = User(
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name,
        is_active=payload.is_active,
        company_id=payload.company_id,
        role=role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    # 1. Busca o usuário pelo email
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha inválidos",
        )

    # 2. Bloqueia acesso caso o usuário esteja inativo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: usuário inativo",
        )

    # 3. Busca e valida status da empresa (quando o usuário está vinculado a uma)
    company = None
    if user.company_id:
        company = db.query(Company).filter(Company.id == user.company_id).first()
        if not company or not company.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado: empresa inativa ou não encontrada",
            )

    # 4. Gera o token e um novo session_id único
    token, session_id = create_access_token(
        data={"sub": str(user.id), "company_id": str(company.id) if company else None, "role": user.role}
    )

    # 5. Sobrescreve a sessão ativa no Redis (derruba qualquer outro login ativo deste usuário)
    save_user_session(employee_id=str(user.id), session_id=session_id)

    return TokenResponse(access_token=token)


@router.patch("/users/{user_id}/role", response_model=UserOut)
def update_user_role(
    user_id: int,
    payload: RoleUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """Promove ou rebaixa um usuário. Só admins podem chamar esta rota."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    user.role = payload.role
    db.commit()
    db.refresh(user)
    return user