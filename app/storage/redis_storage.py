from http.client import HTTPException

import redis
from app.config import settings

# Usa o mesmo Redis do Celery broker, em índice separado (db=2) para não colidir com as filas
_client = redis.from_url(settings.CELERY_BROKER_URL.rsplit("/", 1)[0] + "/2", decode_responses=False)


def save_file(key: str, content: bytes) -> str:
    """Salva o arquivo binário no Redis com expiração automática (TTL)."""
    _client.setex(key, settings.FILE_TTL_SECONDS, content)
    
    try:
        _client.setex(key, settings.FILE_TTL_SECONDS, content)
        return key
    except Exception as e:
        print(f"Erro ao salvar no Redis: {e}")
        raise HTTPException(status_code=503, detail="Serviço de cache/armazenamento temporário indisponível.")


def get_file(key: str) -> bytes | None:
    """Recupera o arquivo do Redis. Retorna None se expirado/inexistente."""
    return _client.get(key)


def delete_file(key: str) -> None:
    _client.delete(key)
