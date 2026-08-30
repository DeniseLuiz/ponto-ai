import fitz  # PyMuPDF
from app.roles.registry import get_role_handler
from app.export.excel_builder import aggregate_and_export_bytes
from app.storage.redis_storage import get_file, save_file, delete_file
from app.config import settings


def split_pdf_text_from_bytes(pdf_bytes: bytes, chunk_size: int) -> list[str]:
    """
    Divide o PDF (em memória) em blocos de texto de N páginas.
    Retorna lista de strings, cada uma correspondente a um bloco.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    total_pages = len(doc)

    if total_pages > settings.MAX_PDF_PAGES:
        doc.close()
        raise ValueError(
            f"PDF possui {total_pages} páginas, "
            f"acima do limite máximo de {settings.MAX_PDF_PAGES}."
        )

    chunks = []
    for start in range(0, total_pages, chunk_size):
        text = ""
        end = min(start + chunk_size, total_pages)
        for page_num in range(start, end):
            text += doc[page_num].get_text()
        chunks.append(text)

    doc.close()
    return chunks


def process_job(job_id: int, pdf_key: str, role_id: int, gemini_client) -> str:
    """
    Orquestra: busca o PDF no Redis -> split em chunks -> chamada ao Gemini
    por chunk (via handler do role) -> agregação em planilha Excel salva
    no Redis. Retorna a chave (result_key) do arquivo gerado.
    """
    pdf_bytes = get_file(pdf_key)
    if pdf_bytes is None:
        raise ValueError("Arquivo PDF expirado ou não encontrado no storage temporário.")

    handler = get_role_handler(role_id)
    chunks = split_pdf_text_from_bytes(pdf_bytes, settings.PDF_CHUNK_SIZE)

    results = []
    for chunk in chunks:
        result_text = handler(chunk, gemini_client)
        results.append(result_text)

    excel_bytes = aggregate_and_export_bytes(results)

    result_key = f"xlsx:{job_id}"
    save_file(result_key, excel_bytes)

    # PDF original não é mais necessário após o processamento
    delete_file(pdf_key)

    return result_key