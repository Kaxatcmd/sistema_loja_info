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
