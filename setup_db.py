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


def main():
    """Função principal"""
    print("Iniciando setup de base de dados...")
    print("="*50)
    criar_base_dados()


if __name__ == '__main__':
    main()
