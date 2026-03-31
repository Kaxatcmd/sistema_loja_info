#!/usr/bin/env python3
"""
Ponto de entrada para setup de base de dados
Cria tabelas e insere dados de teste
"""

import sys
import os

# Adicionar diretório raiz ao Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from setup.database import criar_base_dados
from src.utils.logger import obter_logger

logger = obter_logger(__name__)


def main():
    """Função principal"""
    logger.info("Iniciando setup de base de dados")
    criar_base_dados()


if __name__ == '__main__':
    main()
