"""
Mapeamento central de Role ID -> função de execução.

Para adicionar um novo modo (ex: modo 4):
1. Criar app/roles/role_4_novo.py com uma função execute(text_chunk, gemini_client) -> str
2. Criar app/prompts/role_4.txt com as instruções do novo agente
3. Importar e registrar abaixo em ROLE_REGISTRY
Nenhuma outra parte do sistema precisa ser alterada.
"""
from app.roles import role_1_financeiro, role_2_ponto, role_3_generico

ROLE_REGISTRY = {
    1: role_1_financeiro.execute,
    2: role_2_ponto.execute,
    3: role_3_generico.execute,
}

ROLE_LABELS = {
    1: "Extração Financeira (Holerites / Fichas Financeiras)",
    2: "Extração de Cartão de Ponto (Espelho de Frequência)",
    3: "Modo Genérico / Extensível",
}


def get_role_handler(role_id: int):
    handler = ROLE_REGISTRY.get(role_id)
    if handler is None:
        raise ValueError(f"Role ID {role_id} não está mapeada no registry.")
    return handler


def list_roles():
    return [{"id": k, "label": v} for k, v in ROLE_LABELS.items()]
