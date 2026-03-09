"""
Sistema de Temas e Estilização Profissional
Componentes customizados com design moderno
"""

import tkinter as tk
from tkinter import ttk
from src.config import COLORS, FONTS


class ModernStyle:
    """Gerencia estilos TTk modernos"""
    
    @staticmethod
    def configurar_temas():
        """Configura tema visual para toda a aplicação"""
        style = ttk.Style()
        style.theme_use('clam')  # Tema base mais moderno que 'default'
        
        # === CORES DO TEMA ===
        bg = COLORS['bg']
        bg_sec = COLORS['bg_secondary']
        primary = COLORS['primary']
        primary_light = COLORS['primary_light']
        text_primary = COLORS['text_primary']
        text_secondary = COLORS['text_secondary']
        border = COLORS['border_light']
        
        # === FRAMES ===
        style.configure('TFrame', background=bg)
        style.configure('Accent.TFrame', background=bg_sec, relief='flat')
        style.configure('Header.TFrame', background=COLORS['header_bg'], relief='flat')
        
        # === LABELS ===
        style.configure('TLabel', background=bg, foreground=text_primary, font=FONTS['normal'])
        style.configure('Title.TLabel', background=bg, foreground=primary, 
                       font=FONTS['title'], anchor='center')
        style.configure('Subtitle.TLabel', background=bg, foreground=text_primary, 
                       font=FONTS['subtitle'])
        style.configure('Header.TLabel', background=COLORS['header_bg'], 
                       foreground=text_primary, font=FONTS['large'])
        
        # === BOTÕES ===
        style.configure('TButton', font=FONTS['normal'], borderwidth=0, 
                       relief='flat', padding=10, background=bg_sec)
        style.map('TButton',
                 background=[('active', primary_light), ('pressed', primary)],
                 foreground=[('active', '#ffffff'), ('pressed', '#ffffff')])
        
        # Botão Primário (Azul)
        style.configure('Primary.TButton', font=FONTS['normal'], 
                       borderwidth=1, relief='flat', padding=12, 
                       background=primary, foreground='white')
        style.map('Primary.TButton',
                 background=[('active', primary_light), ('pressed', '#0f3a7d'),
                            ('disabled', COLORS['disabled'])],
                 foreground=[('active', 'white'), ('pressed', 'white'),
                            ('disabled', 'white')])
        
        # Botão Secundário (Contorno)
        style.configure('Secondary.TButton', font=FONTS['normal'], 
                       borderwidth=2, relief='solid', padding=10, 
                       background=bg_sec, foreground=primary)
        style.map('Secondary.TButton',
                 background=[('active', '#f0f4f8'), ('pressed', '#e0e8f0'),
                            ('disabled', bg)],
                 foreground=[('active', primary_light), ('pressed', primary),
                            ('disabled', COLORS['disabled'])],
                 bordercolor=[('focus', primary)])
        
        # Botão Perigo (Vermelho)
        style.configure('Danger.TButton', font=FONTS['normal'], 
                       borderwidth=1, relief='flat', padding=10,
                       background=COLORS['danger'], foreground='white')
        style.map('Danger.TButton',
                 background=[('active', '#f87171'), ('pressed', '#dc2626'),
                            ('disabled', COLORS['disabled'])],
                 foreground=[('active', 'white'), ('pressed', 'white'),
                            ('disabled', 'white')])
        
        # Botão Sucesso (Verde)
        style.configure('Success.TButton', font=FONTS['normal'], 
                       borderwidth=1, relief='flat', padding=10,
                       background=COLORS['success'], foreground='white')
        style.map('Success.TButton',
                 background=[('active', '#34d399'), ('pressed', '#059669'),
                            ('disabled', COLORS['disabled'])],
                 foreground=[('active', 'white'), ('pressed', 'white'),
                            ('disabled', 'white')])
        
        # === ENTRIES ===
        style.configure('TEntry', font=FONTS['normal'], fieldbackground=bg_sec,
                       background=bg_sec, foreground=text_primary, borderwidth=1,
                       relief='solid', padding=8)
        
        # === LABELFRAMES ===
        style.configure('TLabelframe', background=bg, foreground=text_primary,
                       font=FONTS['large'], borderwidth=1, relief='solid')
        style.configure('TLabelframe.Label', background=bg, foreground=primary,
                       font=FONTS['large'])
        
        # === NOTEBOOK (ABAS) ===
        style.configure('TNotebook', background=bg, borderwidth=1)
        style.configure('TNotebook.Tab', font=FONTS['normal'], padding=12)
        style.map('TNotebook.Tab',
                 background=[('selected', bg_sec), ('active', '#f0f4f8')],
                 foreground=[('selected', primary), ('active', text_secondary)])
        
        # === TREEVIEW ===
        style.configure('Treeview', font=FONTS['normal'], background=bg_sec,
                       foreground=text_primary, fieldbackground=bg_sec,
                       borderwidth=1, relief='solid')
        style.configure('Treeview.Heading', font=FONTS['large'],
                       background=primary, foreground='white')
        style.map('Treeview', background=[('selected', primary_light)],
                 foreground=[('selected', 'white')])
        
        # === SCROLLBAR ===
        style.configure('TScrollbar', background=bg_sec, troughcolor=border,
                       arrowcolor=text_secondary, borderwidth=1)
        
        return style


def criar_botao_primario(parent, text, command=None, width=None, **kwargs):
    """
    Cria botão primário estilizado
    
    Args:
        parent: Widget pai
        text: Texto do botão
        command: Função callback
        width: Largura do botão
        **kwargs: Argumentos adicionais
    """
    return ttk.Button(parent, text=text, command=command, style='Primary.TButton',
                     width=width, **kwargs)


def criar_botao_secundario(parent, text, command=None, width=None, **kwargs):
    """
    Cria botão secundário (contorno) estilizado
    
    Args:
        parent: Widget pai
        text: Texto do botão
        command: Função callback
        width: Largura do botão
        **kwargs: Argumentos adicionais
    """
    return ttk.Button(parent, text=text, command=command, style='Secondary.TButton',
                     width=width, **kwargs)


def criar_botao_perigo(parent, text, command=None, width=None, **kwargs):
    """
    Cria botão de perigo (vermelho) estilizado
    
    Args:
        parent: Widget pai
        text: Texto do botão
        command: Função callback
        width: Largura do botão
        **kwargs: Argumentos adicionais
    """
    return ttk.Button(parent, text=text, command=command, style='Danger.TButton',
                     width=width, **kwargs)


def criar_botao_sucesso(parent, text, command=None, width=None, **kwargs):
    """
    Cria botão de sucesso (verde) estilizado
    
    Args:
        parent: Widget pai
        text: Texto do botão
        command: Função callback
        width: Largura do botão
        **kwargs: Argumentos adicionais
    """
    return ttk.Button(parent, text=text, command=command, style='Success.TButton',
                     width=width, **kwargs)


def criar_frame_card(parent, padding=15, bg=None):
    """
    Cria frame estilizado como card
    
    Args:
        parent: Widget pai
        padding: Espaçamento interno
        bg: Cor de fundo (padrão branco)
    
    Returns:
        tk.Frame: Frame estilizado
    """
    frame = tk.Frame(parent, bg=bg or COLORS['bg_secondary'], 
                    relief='flat', borderwidth=1, highlightthickness=1,
                    highlightbackground=COLORS['border_light'])
    frame.pack(fill='both', expand=True, padx=padding, pady=padding)
    return frame


class ModernEntry(ttk.Entry):
    """Entry customizado com placeholder"""
    
    def __init__(self, parent, placeholder="", **kwargs):
        super().__init__(parent, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = COLORS['disabled']
        self.default_color = COLORS['text_primary']
        
        self.bind('<FocusIn>', self._on_focus_in)
        self.bind('<FocusOut>', self._on_focus_out)
        
        self._show_placeholder()
    
    def _show_placeholder(self):
        """Mostra placeholder"""
        if self.placeholder:
            self.insert(0, self.placeholder)
            self.config(foreground=self.placeholder_color)
    
    def _on_focus_in(self, event):
        """Remove placeholder ao receber foco"""
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.config(foreground=self.default_color)
    
    def _on_focus_out(self, event):
        """Recoloca placeholder se vazio"""
        if self.get() == "":
            self._show_placeholder()
    
    def get_value(self):
        """Retorna valor sem placeholder"""
        value = self.get()
        if value == self.placeholder:
            return ""
        return value
