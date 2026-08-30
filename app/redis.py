import redis
from app.config import settings

logger = logging.getLogger("pontoai.redis")

logger.info(f"Tentando conectar ao Redis na URL: {settings.CELERY_BROKER_URL}")
# Reaproveita a mesma URL do broker do Celery, já injetada corretamente pelo
# Render via `fromService` no render.yaml. Antes existia uma segunda conexão
# aqui, montada a partir de REDIS_HOST/REDIS_PORT/REDIS_PASSWORD — variáveis
# que nunca são setadas pelo render.yaml, causando ConnectionError em produção.
try:
    redis_client = redis.Redis.from_url(
        settings.CELERY_BROKER_URL, 
        decode_responses=True,
        socket_connect_timeout=3,
        socket_timeout=3
    )
    # Testa a conexão imediatamente ao subir
    redis_client.ping()
    logger.info("Conexão com o Redis estabelecida com sucesso!")
except Exception as e:
    logger.error(f"FALHA ao conectar no Redis: {e}")
    raise e


def save_user_session(employee_id: str, session_id: str):
    """Salva a sessão sincronizando o TTL com o tempo definido no Environment Group."""
    key = f"user_session:{employee_id}"
    expire_in_seconds = settings.SESSION_EXPIRE_MINUTES * 60
    redis_client.set(key, session_id, ex=expire_in_seconds)
    logger.info("Sessão salva com sucesso")


def get_user_session(employee_id: str) -> str | None:
    """Busca o session_id ativo do usuário no Redis."""
    key = f"user_session:{employee_id}"
    return redis_client.get(key)

print(f"URL do Redis: {settings.CELERY_BROKER_URL}")