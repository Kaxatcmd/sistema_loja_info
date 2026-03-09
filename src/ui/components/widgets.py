"""
Componentes Reutilizáveis
Widgets e componentes customizados
"""

import tkinter as tk
from src.config import COLORS, FONTS


def criar_logo_minimalista(parent):
    """
    Cria logotipo minimalista 'INFO SHOP' como background
    
    Args:
        parent: Widget pai
        
    Returns:
        tk.Canvas: Canvas com o logo
    """
    canvas = tk.Canvas(parent, height=150, bg=COLORS['logo_bg'], highlightthickness=0)
    canvas.pack(fill='x', padx=0, pady=0)
    
    w = 1000
    h = 150
    
    # Texto principal
    canvas.create_text(w/2, h/2, 
                      text="INFO SHOP", 
                      font=("Arial", 80, "bold"), 
                      fill=COLORS['logo_text'], 
                      anchor="center")
    
    # Linha decorativa
    canvas.create_line(w/2 - 300, h - 10, w/2 + 300, h - 10, 
                      fill="#d0d0d0", width=2)
    
    # Círculos decorativos
    circle_size = 30
    canvas.create_oval(w/2 - 350, h/2 - circle_size/2, 
                      w/2 - 350 + circle_size, h/2 + circle_size/2, 
                      outline=COLORS['accent'], width=2)
    canvas.create_oval(w/2 + 320, h/2 - circle_size/2, 
                      w/2 + 320 + circle_size, h/2 + circle_size/2, 
                      outline=COLORS['accent'], width=2)
    
    return canvas
