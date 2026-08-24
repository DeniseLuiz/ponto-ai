import fitz  # PyMuPDF
from app.roles.registry import get_role_handler
from app.export.excel_builder import aggregate_and_export
from app.config import settings


def split_pdf_text(pdf_path: str, chunk_size: int) -> list[str]:
    """
    Divide o PDF em blocos de texto de N páginas (padrão 50).
    Retorna lista de strings, cada uma correspondente a um bloco.
    """
    doc = fitz.open(pdf_path)
    total_pages = len(doc)

    if total_pages > settings.MAX_PDF_PAGES:
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


def process_job(job_id: int, pdf_path: str, role_id: int, gemini_client) -> str:
    """
    Orquestra: split do PDF -> chamada ao Gemini por chunk (via handler do role)
    -> agregação em planilha Excel. Retorna o path do arquivo gerado.
    """
    handler = get_role_handler(role_id)
    chunks = split_pdf_text(pdf_path, settings.PDF_CHUNK_SIZE)

    results = []
    for chunk in chunks:
        result_text = handler(chunk, gemini_client)
        results.append(result_text)

    result_path = aggregate_and_export(results, job_id, settings.STORAGE_DIR)
    return result_path
