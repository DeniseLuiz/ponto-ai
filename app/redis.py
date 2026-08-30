import redis
from app.config import settings

# Reaproveita a mesma URL do broker do Celery, já injetada corretamente pelo
# Render via `fromService` no render.yaml. Antes existia uma segunda conexão
# aqui, montada a partir de REDIS_HOST/REDIS_PORT/REDIS_PASSWORD — variáveis
# que nunca são setadas pelo render.yaml, causando ConnectionError em produção.
redis_client = redis.Redis.from_url(settings.CELERY_BROKER_URL, decode_responses=True)


def save_user_session(employee_id: str, session_id: str):
    """Salva a sessão sincronizando o TTL com o tempo definido no Environment Group."""
    key = f"user_session:{employee_id}"
    expire_in_seconds = settings.SESSION_EXPIRE_MINUTES * 60
    redis_client.set(key, session_id, ex=expire_in_seconds)


def get_user_session(employee_id: str) -> str | None:
    """Busca o session_id ativo do usuário no Redis."""
    key = f"user_session:{employee_id}"
    return redis_client.get(key)
