import uuid
import io
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app import models, schemas
from app.auth.security import get_current_user
from app.roles.registry import list_roles
from app.jobs.tasks import run_extraction_job
from app.storage.redis_storage import save_file, get_file

# router = APIRouter(prefix="/jobs", tags=["Processamento (Jobs)"])
router = APIRouter(tags=["Processamento (Jobs)"])


@router.get("/roles")
def get_available_roles():
    """Lista os modos (roles) disponíveis para o frontend montar os botões dinamicamente."""
    return list_roles()


@router.post("/upload", response_model=schemas.JobOut, status_code=202)
async def upload_pdf(
    file: UploadFile = File(...),
    role_id: int = Form(...),
    employee_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Recebe o PDF, salva no Redis (com TTL) e dispara o processamento
    assíncrono via Celery. Retorna imediatamente o job criado (status=pending).
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF são aceitos.")

    if role_id not in (1, 2, 3):
        raise HTTPException(status_code=400, detail="role_id inválido. Use 1, 2 ou 3.")

    content = await file.read()
    pdf_key = f"pdf:{uuid.uuid4().hex}"
    save_file(pdf_key, content)

    job = models.Job(
        employee_id=employee_id,
        user_id=current_user.id,
        role_mode=role_id,
        original_filename=file.filename,
        pdf_key=pdf_key,
        status="pending",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Dispara a tarefa assíncrona (Celery worker)
    run_extraction_job.delay(job.id)

    return job


@router.get("/", response_model=List[schemas.JobOut])
def list_jobs(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.query(models.Job).filter(models.Job.user_id == current_user.id).all()


@router.get("/{job_id}/status", response_model=schemas.JobOut)
def job_status(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    job = db.query(models.Job).filter(
        models.Job.id == job_id, models.Job.user_id == current_user.id
    ).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job não encontrado.")
    return job


@router.get("/{job_id}/download")
def download_result(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    job = db.query(models.Job).filter(
        models.Job.id == job_id, models.Job.user_id == current_user.id
    ).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job não encontrado.")
    if job.status != "done" or not job.result_key:
        raise HTTPException(status_code=409, detail="Job ainda não foi concluído.")

    file_bytes = get_file(job.result_key)
    if file_bytes is None:
        raise HTTPException(
            status_code=410,
            detail="Arquivo expirado no storage temporário. Reprocesse o job enviando o PDF novamente.",
        )

    return StreamingResponse(
        io.BytesIO(file_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=resultado_job_{job.id}.xlsx"},
    )
