import redis
from app.config import settings

# Conexão usando todas as variáveis mapeadas do ambiente
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True
)

def save_user_session(employee_id: str, session_id: str):
    """Salva a sessão sincronizando o TTL com o tempo definido no Environment Group."""
    key = f"user_session:{employee_id}"
    # Converte os minutos do Environment Group em segundos para o Redis
    expire_in_seconds = settings.SESSION_EXPIRE_MINUTES * 60
    redis_client.set(key, session_id, ex=expire_in_seconds)

def get_user_session(employee_id: str) -> str | None:
    """Busca o session_id ativo do usuário no Redis."""
    key = f"user_session:{employee_id}"
    return redis_client.get(key)