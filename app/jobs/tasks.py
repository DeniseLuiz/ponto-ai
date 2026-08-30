from datetime import datetime
import google.generativeai as genai

from app.celery_app import celery_app
from app.database import SessionLocal
from app import models
from app.jobs.processor import process_job
from app.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)


@celery_app.task(name="run_extraction_job", bind=True, max_retries=2)
def run_extraction_job(self, job_id: int):
    db = SessionLocal()
    try:
        job = db.query(models.Job).get(job_id)
        if not job:
            return

        job.status = "processing"
        db.commit()

        client = genai.GenerativeModel(settings.GEMINI_MODEL)
        result_key = process_job(job_id, job.pdf_key, job.role_mode, client)

        job.result_key = result_key
        job.status = "done"
        job.finished_at = datetime.utcnow()
        db.commit()

    except Exception as e:
        db.rollback()
        # Reabre sessão limpa para registrar a falha caso ocorra erro no BD
        job = db.query(models.Job).get(job_id)
        if job:
            job.status = "failed"
            job.error_message = str(e)
            job.finished_at = datetime.utcnow()
            db.commit()
        raise e

    finally:
        db.close()