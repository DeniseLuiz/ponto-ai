# PontoAI — Extração de Cartões de Ponto e Fichas Financeiras via IA

## O que é
API + processamento assíncrono para extrair dados estruturados (ponto e
financeiro) de PDFs de até 5000 páginas, usando Gemini 2.5 Pro, com saída
em planilha Excel.

## Como rodar (passo a passo)

### 1. Pré-requisitos
- Docker e Docker Compose instalados.
- Uma API Key do Google Gemini (https://aistudio.google.com/apikey).

### 2. Configurar variáveis de ambiente
```bash
cp .env.example .env
# edite o .env e preencha GEMINI_API_KEY e JWT_SECRET

# TODO
# Replicar logo CSS e imagem no head da página
# Testar a aplicação de ponta a ponta
# Ajustar possíveis endpoints 
# Validar o consumo de IA, armazenamento e outras infras
#Retirar os 'melhorias adicionadas'
#Adicionar novo layout da marca
#Pemitir interromper o envio se necessário (ou clicando no botão laranja, ou cliando no fechar do arquivo)
#adicionar um descritivo de cada um dos modos disponíveis na aplicação
