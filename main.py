#!/usr/bin/env python3
"""
Ponto de entrada raiz da aplicação
Inicia o Sistema de Loja de Informática
"""

import sys
import os

# Adicionar diretório raiz ao Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from src.ui.app import LojaApp


def main():
    """Função principal"""
    root = tk.Tk()
    app = LojaApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
