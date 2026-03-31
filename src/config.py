"""
Configurações da aplicação.

As variáveis sensíveis são carregadas a partir do ficheiro .env
(ver .env.example para referência). Se o ficheiro não existir ou
uma variável não estiver definida, são usados valores de fallback
para facilitar o desenvolvimento local.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Caminho raiz do projecto (dois níveis acima deste ficheiro: src/ → raiz)
_BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega o ficheiro .env da raíz do projecto, se existir
load_dotenv(_BASE_DIR / ".env")


def _env(chave: str, padrao: str = "") -> str:
    """
    Lê uma variável de ambiente com fallback para o valor padrão.

    Args:
        chave (str): Nome da variável de ambiente.
        padrao (str): Valor usado quando a variável não está definida.

    Returns:
        str: Valor da variável ou o valor padrão.
    """
    return os.environ.get(chave, padrao)


# Base de Dados
DATABASE_CONFIG = {
    'host':     _env("DB_HOST",     "localhost"),
    'user':     _env("DB_USER",     "root"),
    'password': _env("DB_PASSWORD", ""),
    'database': _env("DB_NAME",     "loja_informatica"),
}

# Chave secreta da aplicação (usada para hashing, tokens, etc.)
SECRET_KEY: str = _env("SECRET_KEY", "chave_padrao_insegura_substitua_em_producao")

# Tamanho do pool de conexões (Melhoria 10)
DB_POOL_SIZE: int = int(_env("DB_POOL_SIZE", "5"))

# Stock mínimo de alerta — produtos com stock inferior a este valor
# geram notificações no painel de administração.
STOCK_MINIMO: int = int(_env("STOCK_MINIMO", "5"))

# GUI
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
APP_TITLE = "Sistema de Loja de Informática"

# Estilos - Tipografia
FONTS = {
    'title': ("Segoe UI", 24, "bold"),
    'subtitle': ("Segoe UI", 16, "bold"),
    'large': ("Segoe UI", 13, "bold"),
    'normal': ("Segoe UI", 11),
    'small': ("Segoe UI", 10),
    'mono': ("Consolas", 9),
}

# Paleta de Cores Profissional
COLORS = {
    # Cores principais
    'primary': '#1e40af',        # Azul escuro profissional
    'primary_light': '#3b82f6',  # Azul claro
    'primary_dark': '#0f172a',   # Azul muito escuro (quase preto)
    
    # Cores secundárias
    'success': '#10b981',        # Verde
    'danger': '#ef4444',         # Vermelho
    'warning': '#f59e0b',        # Amarelo/Laranja
    'info': '#06b6d4',           # Ciano
    
    # Neutras
    'bg': '#f8fafc',             # Fundo muito claro
    'bg_secondary': '#ffffff',   # Branco puro
    'text_primary': '#0f172a',   # Texto escuro
    'text_secondary': '#475569', # Texto cinzento
    'border': '#cbd5e1',         # Borda cinzenta clara
    'border_light': '#e2e8f0',   # Borda mais clara
    'disabled': '#94a3b8',       # Desabilitado
    
    # Logo e Header
    'logo_bg': '#1e40af',
    'logo_text': '#ffffff',
    'header_bg': '#ffffff',
}

# Validação
PASSWORD_MIN_LENGTH = 6
EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
PRODUTO_NOME_MAX_LENGTH = 100
