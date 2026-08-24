import openpyxl
from io import BytesIO


def aggregate_and_export_bytes(results: list[str]) -> bytes:
    """
    Recebe a lista de textos (um por chunk processado pelo Gemini, no formato
    TAB-separated) e monta um único arquivo .xlsx, retornando os bytes
    (em vez de salvar em disco).
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Resultado"

    alerts = []

    for block in results:
        if not block:
            continue
        for line in block.strip().splitlines():
            line = line.strip()
            if not line:
                continue
            # Detecta linhas de alerta (não tabulares) e as separa
            if "\t" not in line:
                alerts.append(line)
                continue
            row = line.split("\t")
            ws.append(row)

    if alerts:
        alert_ws = wb.create_sheet("Alertas")
        for i, alert in enumerate(alerts, start=1):
            alert_ws.cell(row=i, column=1, value=alert)

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.read()
