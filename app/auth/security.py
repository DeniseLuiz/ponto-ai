import uuid
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt
from passlib.context import CryptContext
from app.config import settings
from app.database import get_db
from app.models import User
from app.redis import get_user_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> tuple[str, str]:
    """Gera o JWT e um session_id novo, embutido no próprio token.
    Retorna (token, session_id)."""
    session_id = str(uuid.uuid4())
    to_encode = data.copy()
    to_encode["session_id"] = session_id
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.SESSION_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token, session_id


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        session_id: str = payload.get("session_id")
        if user_id is None or session_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    # Compara com a sessão ativa no Redis: um login mais recente sobrescreve
    # essa chave, derrubando qualquer token anterior mesmo que ainda não tenha expirado.
    active_session = get_user_session(user_id)
    if active_session != session_id:
        raise credentials_exception

    return {
        "id": int(user_id),
        "session_id": session_id,  # adicione outras informações do payload se precisar (ex: email, role)
    }


# Alias para manter compatibilidade caso algum arquivo chame verify_active_session
verify_active_session = get_current_user


def require_admin(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Dependency para rotas restritas a administradores.
    Reaproveita get_current_user (token + sessão já validados) e só confere o role."""
    # user = db.query(User).filter(User.id == int(current_user["sub"])).first()
    user = db.query(User).filter(User.id == current_user["id"]).first()
    if not user or user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso restrito a administradores")
    return user