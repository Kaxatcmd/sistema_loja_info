"""
Configurações da aplicação
"""

# Base de Dados
DATABASE_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'loja_informatica'
}

# GUI
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
APP_TITLE = "⌂ Sistema de Loja de Informática"

# Estilos
FONTS = {
    'title': ("Arial", 22, "bold"),
    'large': ("Arial", 14, "bold"),
    'normal': ("Arial", 11),
    'small': ("Arial", 10),
    'mono': ("Courier", 9),
}

COLORS = {
    'bg': '#f0f0f0',
    'logo_bg': "#90D7EC",
    'logo_text': "#2a71b4",
    'accent': "#fbffff",
}

# Validação
PASSWORD_MIN_LENGTH = 6
EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
PRODUTO_NOME_MAX_LENGTH = 100
