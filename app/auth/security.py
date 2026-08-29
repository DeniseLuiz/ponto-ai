import uuid
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from app.config import settings
from app.redis import get_user_session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict) -> tuple[str, str]:
    to_encode = data.copy()
    session_id = str(uuid.uuid4())
    
    # Tempo do JWT idêntico ao TTL configurado para o Redis
    expire = datetime.utcnow() + timedelta(minutes=settings.SESSION_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "session_id": session_id})
    
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token, session_id

def verify_active_session(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sessão inválida ou expirada",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        employee_id: str = payload.get("sub")
        session_id: str = payload.get("session_id")
        
        if not employee_id or not session_id:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception

    # Validação no Redis
    current_active_session = get_user_session(employee_id)
    if not current_active_session or current_active_session != session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessão encerrada por um novo login em outro dispositivo"
        )

    return payload

get_current_user = verify_active_session