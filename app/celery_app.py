from celery import Celery
from app.config import settings

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
