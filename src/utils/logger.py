"""
Sistema de Logging da Aplicação.

Configura um logger centralizado com ``RotatingFileHandler`` que grava
em ``logs/app.log``. A pasta ``logs/`` é criada automaticamente.

Formato de cada linha::

    [2026-03-27 14:32:01] [INFO ] [src.ui.screens.login] — Login bem-sucedido: admin@example.com

Utilização noutros módulos::

    from src.utils.logger import obter_logger
    logger = obter_logger(__name__)

    logger.info("Mensagem informativa")
    logger.warning("Atenção!")
    logger.error("Algo correu mal: %s", str(e))
"""

import logging
import logging.handlers
from pathlib import Path

# ------------------------------------------------------------------
# Constantes de configuração
# ------------------------------------------------------------------

# Caminho raiz do projecto (dois níveis acima de src/utils/)
_RAIZ = Path(__file__).resolve().parent.parent.parent

# Directório onde os logs são guardados
PASTA_LOGS: Path = _RAIZ / "logs"

# Ficheiro principal de log
FICHEIRO_LOG: Path = PASTA_LOGS / "app.log"

# Tamanho máximo por ficheiro de log (5 MB)
TAMANHO_MAXIMO: int = 5 * 1024 * 1024  # 5 MB em bytes

# Número de ficheiros de backup a manter
NUM_BACKUPS: int = 3

# Nome do logger raiz da aplicação
NOME_LOGGER: str = "loja"

# Formato das mensagens: [TIMESTAMP] [NÍVEL ] [MÓDULO] — Mensagem
_FORMATO = "[%(asctime)s] [%(levelname)-5s] [%(name)s] — %(message)s"
_FORMATO_DATA = "%Y-%m-%d %H:%M:%S"


def _configurar_logger() -> logging.Logger:
    """
    Cria e configura o logger raiz da aplicação.

    Apenas deve ser chamado uma vez (na importação deste módulo).
    Configura dois handlers:
        - ``RotatingFileHandler``: grava em ``logs/app.log``
        - ``StreamHandler``: exibe no terminal (nível WARNING ou superior)

    Returns:
        logging.Logger: Logger configurado pronto a usar.
    """
    # Garantir que a pasta logs/ existe
    PASTA_LOGS.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(NOME_LOGGER)

    # Evitar configurar múltiplas vezes (ex.: reimportação em testes)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    formatador = logging.Formatter(fmt=_FORMATO, datefmt=_FORMATO_DATA)

    # Handler rotativo para ficheiro
    handler_ficheiro = logging.handlers.RotatingFileHandler(
        filename=FICHEIRO_LOG,
        maxBytes=TAMANHO_MAXIMO,
        backupCount=NUM_BACKUPS,
        encoding="utf-8",
    )
    handler_ficheiro.setLevel(logging.DEBUG)
    handler_ficheiro.setFormatter(formatador)

    # Handler para o terminal (apenas avisos e erros)
    handler_consola = logging.StreamHandler()
    handler_consola.setLevel(logging.WARNING)
    handler_consola.setFormatter(formatador)

    logger.addHandler(handler_ficheiro)
    logger.addHandler(handler_consola)

    return logger


# Logger raiz — criado na importação do módulo
_logger_raiz = _configurar_logger()


def obter_logger(nome_modulo: str) -> logging.Logger:
    """
    Devolve um logger filho do logger raiz da aplicação.

    O nome do módulo é usado como identificador na mensagem de log,
    facilitando a identificação da origem de cada evento.

    Args:
        nome_modulo (str): Normalmente ``__name__`` do módulo chamador.

    Returns:
        logging.Logger: Logger pronto a usar.

    Exemplo::

        from src.utils.logger import obter_logger
        logger = obter_logger(__name__)
        logger.info("Módulo iniciado")
    """
    # Se o nome já começa pelo prefixo da aplicação, usa directamente;
    # caso contrário, cria filho do logger raiz para herdar handlers.
    if nome_modulo.startswith(NOME_LOGGER):
        return logging.getLogger(nome_modulo)
    return logging.getLogger(f"{NOME_LOGGER}.{nome_modulo}")
