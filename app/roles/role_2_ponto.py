from pathlib import Path

PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "role_2.txt"


def load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def execute(text_chunk: str, gemini_client) -> str:
    """Modo 2: Extração de cartão de ponto / espelho de frequência."""
    prompt = load_prompt()
    full_prompt = f"{prompt}\n\n--- TRECHO DO DOCUMENTO ---\n{text_chunk}"
    response = gemini_client.generate_content(full_prompt)
    return response.text or ""
