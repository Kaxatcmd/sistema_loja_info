"""
Aplicação Principal - LojaApp
Orquestrador da interface gráfica: autenticação e navegação entre vistas.
"""

import tkinter as tk
from tkinter import ttk
from src.config import FONTS, COLORS, WINDOW_WIDTH, WINDOW_HEIGHT, APP_TITLE
from src.ui.screens.login import LoginScreen
from src.ui.screens.register import RegisterScreen
from src.ui.theme import ModernStyle
from src.ui.notifications import NotificationManager
from src.ui.views.cliente_view import ClienteView
from src.ui.views.admin_view import AdminView


class LojaApp:
    """Aplicação Principal da Loja — orquestra autenticação e vistas."""

    def __init__(self, master):
        self.master = master
        self.master.title(APP_TITLE)
        self.master.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.master.configure(bg=COLORS['bg'])

        ModernStyle.configurar_temas()

        self.notify = NotificationManager(self.master)

        self.db = None
        self.usuario_atual = None
        self.carrinho = []

        self.mostrar_login()

    # ------------------------------------------------------------------ #
    #  Autenticação                                                        #
    # ------------------------------------------------------------------ #

    def mostrar_login(self):
        """Exibe tela de login."""
        login = LoginScreen(self.master, self.on_login_success, self.mostrar_registo, self.notify)
        login.show()

    def mostrar_registo(self):
        """Exibe tela de registo."""
        register = RegisterScreen(self.master, self.on_register_success, self.mostrar_login, self.notify)
        register.show()

    def on_register_success(self):
        """Callback executado após registo bem-sucedido."""
        self.mostrar_login()

    def on_login_success(self, usuario_cliente, db):
        """Callback executado após login bem-sucedido."""
        self.usuario_atual = usuario_cliente
        self.db = db

        # Garantir tabela de avaliações existe (migração automática)
        self.db.executar_update("""
            CREATE TABLE IF NOT EXISTS avaliacoes (
                id_avaliacao INT PRIMARY KEY AUTO_INCREMENT,
                id_cliente INT NOT NULL,
                id_produto INT NOT NULL,
                estrelas TINYINT NOT NULL,
                data_avaliacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY uq_cliente_produto (id_cliente, id_produto),
                FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
                FOREIGN KEY (id_produto) REFERENCES produtos(id_produto)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        if usuario_cliente.is_admin:
            self.criar_interface_admin()
        else:
            self.criar_interface_cliente()

    # ------------------------------------------------------------------ #
    #  Navegação de vistas                                                 #
    # ------------------------------------------------------------------ #

    def limpar_janela(self):
        """Remove todos os widgets da janela principal (exceto notification_frame)."""
        for widget in self.master.winfo_children():
            if widget != self.notify.notification_frame:
                widget.destroy()

    def criar_interface_cliente(self):
        """Cria e apresenta a vista do cliente."""
        self.limpar_janela()
        self.master.configure(bg=COLORS['bg'])
        ClienteView(self.master, self).criar_interface()

    def criar_interface_admin(self):
        """Cria e apresenta a vista do administrador."""
        self.limpar_janela()
        self.master.configure(bg=COLORS['bg'])
        AdminView(self.master, self).criar_interface()

    # ------------------------------------------------------------------ #
    #  Logout                                                              #
    # ------------------------------------------------------------------ #

    def fazer_logout(self):
        """Realiza logout do utilizador."""
        self.usuario_atual = None
        self.carrinho = []
        if self.db:
            self.db.desconectar()
            self.db = None
        self.mostrar_login()

    # ------------------------------------------------------------------ #
    #  Popup partilhado: Detalhes de produto                               #
    # ------------------------------------------------------------------ #

    def _mostrar_detalhes_produto(self, produto, media_avaliacao=None, num_avaliacoes=0):
        """Abre popup com informação detalhada do produto (usado por cliente e admin)."""
        janela = tk.Toplevel(self.master)
        janela.title(f"📦 {produto.nome}")
        janela.geometry("520x420")
        janela.configure(bg=COLORS['bg'])
        janela.resizable(False, False)
        janela.grab_set()

        frame_header = tk.Frame(janela, bg=COLORS['primary'], pady=15)
        frame_header.pack(fill='x')
        tk.Label(
            frame_header, text=produto.nome, font=FONTS['subtitle'],
            fg='white', bg=COLORS['primary'],
        ).pack(padx=20)

        frame_body = tk.Frame(janela, bg=COLORS['bg'])
        frame_body.pack(fill='both', expand=True, padx=25, pady=20)

        tk.Label(
            frame_body, text=f"💵 Preço: €{produto.preco:.2f}",
            font=FONTS['large'], fg=COLORS['success'], bg=COLORS['bg'],
        ).pack(anchor='w')

        tk.Label(
            frame_body, text=f"📦 Stock disponível: {produto.stock} unidades",
            font=FONTS['normal'], fg=COLORS['text_secondary'], bg=COLORS['bg'],
        ).pack(anchor='w', pady=(5, 10))

        if media_avaliacao is not None:
            filled = round(media_avaliacao)
            stars = '★' * filled + '☆' * (5 - filled)
            av_text = (
                f"⭐ Avaliação: {stars} {media_avaliacao:.1f}/5  "
                f"({num_avaliacoes} avaliação{'ões' if num_avaliacoes != 1 else ''})"
            )
            tk.Label(
                frame_body, text=av_text,
                font=FONTS['normal'], fg='#d97706', bg=COLORS['bg'],
            ).pack(anchor='w', pady=(0, 10))
        else:
            tk.Label(
                frame_body, text="⭐ Avaliação: ☆☆☆☆☆  (ainda sem avaliações)",
                font=FONTS['normal'], fg=COLORS['text_secondary'], bg=COLORS['bg'],
            ).pack(anchor='w', pady=(0, 10))

        ttk.Separator(frame_body, orient='horizontal').pack(fill='x', pady=8)

        tk.Label(
            frame_body, text="📄 Descrição:",
            font=FONTS['normal'], fg=COLORS['text_primary'], bg=COLORS['bg'],
        ).pack(anchor='w')
        desc = produto.descricao if produto.descricao else "Sem descrição disponível."
        tk.Label(
            frame_body, text=desc, font=FONTS['small'],
            fg=COLORS['text_secondary'], bg=COLORS['bg'],
            wraplength=460, justify='left',
        ).pack(anchor='w', pady=(5, 0))

        tk.Button(
            janela, text="✖ Fechar", command=janela.destroy,
            font=FONTS['normal'], bg=COLORS['danger'], fg='white',
            relief='flat', padx=25, pady=8, cursor='hand2',
            activebackground='#dc2626',
        ).pack(pady=15)
