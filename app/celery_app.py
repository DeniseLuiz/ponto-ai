from celery import Celery
from app.config import settings
import ssl

celery_app = Celery(
    "pontoai",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.jobs.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
    task_track_started=True,
    worker_max_tasks_per_child=20,  # evita acúmulo de memória em PDFs grandes
)

# Se a URL do Redis usar TLS (rediss://), o Celery exige ssl_cert_reqs
# explicitamente — sem isso, ele recusa iniciar (ValueError). Isso é inofensivo
# quando a URL é redis:// comum (sem TLS): esses parâmetros simplesmente são
# ignorados nesse caso.
if settings.CELERY_BROKER_URL.startswith("rediss://"):
    celery_app.conf.broker_use_ssl = {"ssl_cert_reqs": ssl.CERT_NONE}
if settings.CELERY_RESULT_BACKEND.startswith("rediss://"):
    celery_app.conf.redis_backend_use_ssl = {"ssl_cert_reqs": ssl.CERT_NONE}
