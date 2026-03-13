"""
Componentes Reutilizáveis
Widgets e componentes customizados com design profissional
"""

import tkinter as tk
from tkinter import ttk
from src.config import COLORS, FONTS


def criar_logo_minimalista(parent):
    """
    Cria logotipo profissional moderno
    
    Args:
        parent: Widget pai
        
    Returns:
        tk.Canvas: Canvas com o logo
    """
    canvas = tk.Canvas(parent, height=120, bg=COLORS['logo_bg'], 
                      highlightthickness=0)
    canvas.pack(fill='x', padx=0, pady=0)
    
    w = 1000
    h = 120
    
    # Texto principal
    canvas.create_text(w/2, h/2 + 5, 
                      text="🛒 INFO SHOP", 
                      font=("Segoe UI", 48, "bold"), 
                      fill=COLORS['logo_text'], 
                      anchor="center")
    
    # # Linha decorativa inferior
    # canvas.create_line(50, h - 3, w - 50, h - 3, 
    #                   fill=COLORS['logo_text'], width=2)
    
    return canvas


def criar_header_executivo(parent, titulo="", usuario="", callback_logout=None):
    """
    Cria header executivo com branding
    
    Args:
        parent: Widget pai
        titulo: Título do header
        usuario: Nome do usuário
        callback_logout: Função para logout
        
    Returns:
        tk.Frame: Frame do header
    """
    frame = tk.Frame(parent, bg=COLORS['header_bg'], height=70, 
                    relief='flat', borderwidth=0)
    frame.pack(fill='x', padx=0, pady=0)
    frame.pack_propagate(False)
    
    # Container interno com padding
    container = tk.Frame(frame, bg=COLORS['header_bg'])
    container.pack(fill='both', expand=True, padx=20, pady=12)
    
    # Lado esquerdo - Título
    frame_left = tk.Frame(container, bg=COLORS['header_bg'])
    frame_left.pack(side='left', fill='both', expand=True)
    
    if titulo:
        lbl_titulo = tk.Label(frame_left, text=titulo, 
                             font=FONTS['large'], fg=COLORS['primary'],
                             bg=COLORS['header_bg'])
        lbl_titulo.pack(anchor='w')
    
    if usuario:
        lbl_usuario = tk.Label(frame_left, text=f"Usuário: {usuario}", 
                              font=FONTS['small'], fg=COLORS['text_secondary'],
                              bg=COLORS['header_bg'])
        lbl_usuario.pack(anchor='w')
    
    # Lado direito - Botão Logout
    if callback_logout:
        frame_right = tk.Frame(container, bg=COLORS['header_bg'])
        frame_right.pack(side='right', fill='y')
        
        btn = tk.Button(frame_right, text="🚪 Logout",
                       command=callback_logout,
                       font=FONTS['normal'],
                       fg='white',
                       bg=COLORS['danger'],
                       relief='flat',
                       padx=15, pady=8,
                       cursor='hand2',
                       activebackground='#dc2626')
        btn.pack(side='right')
    
    # Linha separadora
    separador = tk.Frame(frame, bg=COLORS['border_light'], height=1)
    separador.pack(fill='x', side='bottom')
    
    return frame


def criar_card_info(parent, titulo="", conteudo="", icone=""):
    """
    Cria card informativo
    
    Args:
        parent: Widget pai
        titulo: Título do card
        conteudo: Conteúdo do card
        icone: Ícone/emoji
        
    Returns:
        tk.Frame: Frame do card
    """
    # Card background
    card = tk.Frame(parent, bg=COLORS['bg_secondary'], relief='flat',
                   borderwidth=1, highlightthickness=1,
                   highlightbackground=COLORS['border_light'])
    card.pack(fill='both', expand=True, padx=10, pady=5)
    
    # Conteúdo
    container = tk.Frame(card, bg=COLORS['bg_secondary'])
    container.pack(fill='both', expand=True, padx=15, pady=12)
    
    if icone or titulo:
        header = tk.Frame(container, bg=COLORS['bg_secondary'])
        header.pack(fill='x', pady=(0, 8))
        
        if icone:
            lbl_icone = tk.Label(header, text=icone, font=("Arial", 20),
                                bg=COLORS['bg_secondary'])
            lbl_icone.pack(side='left', padx=(0, 8))
        
        if titulo:
            lbl_titulo = tk.Label(header, text=titulo, font=FONTS['large'],
                                 fg=COLORS['primary'], bg=COLORS['bg_secondary'])
            lbl_titulo.pack(side='left', fill='x', expand=True)
    
    if conteudo:
        lbl_conteudo = tk.Label(container, text=conteudo, font=FONTS['normal'],
                               fg=COLORS['text_secondary'], bg=COLORS['bg_secondary'],
                               justify='left', wraplength=300)
        lbl_conteudo.pack(fill='both', expand=True)
    
    return card


def criar_campo_formulario(parent, label_texto="", tooltip=None):
    """
    Cria campo de formulário completo com label
    
    Args:
        parent: Widget pai
        label_texto: Texto do label
        tooltip: Texto de ajuda
        
    Returns:
        Tuple: (frame_pai, entry_widget)
    """
    frame = tk.Frame(parent, bg=COLORS['bg'])
    frame.pack(fill='x', padx=0, pady=8)
    
    # Label
    if label_texto:
        header = tk.Frame(frame, bg=COLORS['bg'])
        header.pack(fill='x', padx=0, pady=(0, 4))
        
        lbl = tk.Label(header, text=label_texto, font=FONTS['normal'],
                      fg=COLORS['text_primary'], bg=COLORS['bg'])
        lbl.pack(anchor='w')
        
        if tooltip:
            tooltip_lbl = tk.Label(header, text=tooltip, font=FONTS['small'],
                                  fg=COLORS['text_secondary'], bg=COLORS['bg'])
            tooltip_lbl.pack(anchor='w', padx=(0, 0))
    
    # Entry
    entry = ttk.Entry(frame, width=40, font=FONTS['normal'])
    entry.pack(fill='x', padx=0)
    
    return frame, entry


def criar_linha_dados(parent, label="", valor="", destaque=False):
    """
    Cria linha de exibição de dados
    
    Args:
        parent: Widget pai
        label: Rótulo
        valor: Valor a exibir
        destaque: Se deve destacar o valor
        
    Returns:
        tk.Frame: Frame da linha
    """
    frame = tk.Frame(parent, bg=COLORS['bg_secondary'])
    frame.pack(fill='x', padx=10, pady=5)
    
    # Label
    if label:
        lbl = tk.Label(frame, text=f"{label}:", font=FONTS['normal'],
                      fg=COLORS['text_secondary'], bg=COLORS['bg_secondary'])
        lbl.pack(side='left')
    
    # Valor
    cor_valor = COLORS['primary'] if destaque else COLORS['text_primary']
    peso = 'bold' if destaque else 'normal'
    lbl_valor = tk.Label(frame, text=valor, font=(FONTS['normal'][0], 
                                                    FONTS['normal'][1], peso),
                        fg=cor_valor, bg=COLORS['bg_secondary'])
    lbl_valor.pack(side='left', padx=10)
    
    return frame


def criar_tabela_simples(parent, colunas, dados):
    """
    Cria tabela simples com Treeview
    
    Args:
        parent: Widget pai
        colunas: Lista de nomes de colunas
        dados: Lista de tuplas com dados
        
    Returns:
        ttk.Treeview: Widget da tabela
    """
    # Frame container
    frame = tk.Frame(parent, bg=COLORS['bg'])
    frame.pack(fill='both', expand=True, padx=10, pady=10)
    
    # Treeview
    tree = ttk.Treeview(frame, columns=colunas, height=10, show='headings',
                       style='Treeview')
    
    # Define colunas
    for col in colunas:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor='center')
    
    # Insere dados
    for row in dados:
        tree.insert("", "end", values=row)
    
    # Scrollbar
    scrollbar = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    # Layout
    tree.grid(row=0, column=0, sticky='nsew')
    scrollbar.grid(row=0, column=1, sticky='ns')
    
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)
    
    return tree


def criar_painel_lateral(parent, titulo=""):
    """
    Cria painel lateral estilizado
    
    Args:
        parent: Widget pai
        titulo: Título do painel
        
    Returns:
        tk.Frame: Frame do painel
    """
    frame = tk.Frame(parent, bg=COLORS['bg_secondary'], relief='flat',
                    borderwidth=1, highlightthickness=1,
                    highlightbackground=COLORS['border_light'])
    frame.pack(side='left', fill='both', padx=10, pady=10)
    
    # Cabeçalho com cor
    if titulo:
        header = tk.Frame(frame, bg=COLORS['primary'], height=35)
        header.pack(fill='x', padx=0, pady=0)
        header.pack_propagate(False)
        
        lbl = tk.Label(header, text=titulo, font=FONTS['large'],
                      fg='white', bg=COLORS['primary'])
        lbl.pack(fill='both', expand=True, padx=12, pady=8)
    
    return frame


def criar_separador(parent, orient='horizontal'):
    """
    Cria linha separadora
    
    Args:
        parent: Widget pai
        orient: 'horizontal' ou 'vertical'
    
    Returns:
        tk.Frame: Separador
    """
    if orient == 'horizontal':
        sep = tk.Frame(parent, height=1, bg=COLORS['border_light'])
        sep.pack(fill='x', padx=0, pady=10)
    else:
        sep = tk.Frame(parent, width=1, bg=COLORS['border_light'])
        sep.pack(fill='y', padx=10, pady=0)
    return sep


