import logging
import sys

# Configuração básica do logging para exibir no console do Render
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger("pontoai")
logger.setLevel(logging.INFO)