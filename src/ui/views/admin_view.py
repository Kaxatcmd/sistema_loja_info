"""
Vista do Administrador
Abas de gestão de produtos, clientes e histórico de vendas.
"""

import tkinter as tk
from tkinter import ttk

from src.config import FONTS, COLORS
from src.models.produto import Produto
from src.models.cliente import Cliente
from src.utils.validators import validar_nome_produto, validar_preco, validar_stock
from src.ui.components.widgets import criar_header_executivo


class AdminView:
    """Interface em abas para o administrador autenticado."""

    def __init__(self, master, app):
        """
        Args:
            master: Janela raiz Tkinter.
            app:    Instância de LojaApp — fornece db, usuario_atual, notify.
        """
        self.master = master
        self.app = app

    # ------------------------------------------------------------------ #
    #  Ponto de entrada                                                    #
    # ------------------------------------------------------------------ #

    def criar_interface(self):
        """Monta o header e o notebook com as três abas do administrador."""
        criar_header_executivo(
            self.master,
            titulo=f"👨‍💼 Painel Administrativo - {self.app.usuario_atual.nome}",
            usuario="Modo Administrador",
            callback_logout=self.app.fazer_logout,
        )

        notebook = ttk.Notebook(self.master)
        notebook.pack(fill='both', expand=True, padx=15, pady=15)

        frame_produtos = ttk.Frame(notebook)
        notebook.add(frame_produtos, text="📦 Gerir Produtos")
        self._criar_aba_gerir_produtos(frame_produtos)

        frame_clientes = ttk.Frame(notebook)
        notebook.add(frame_clientes, text="👥 Gerir Clientes")
        self._criar_aba_gerir_clientes(frame_clientes)

        frame_vendas = ttk.Frame(notebook)
        notebook.add(frame_vendas, text="📊 Ver Vendas")
        self._criar_aba_vendas(frame_vendas)

    # ------------------------------------------------------------------ #
    #  Aba 1 — Gerir Produtos                                              #
    # ------------------------------------------------------------------ #

    def _criar_aba_gerir_produtos(self, parent):
        for widget in parent.winfo_children():
            widget.destroy()

        tk.Label(
            parent, text="Lista de Produtos",
            font=FONTS['subtitle'], fg=COLORS['primary'], bg=COLORS['bg'],
        ).pack(anchor='w', padx=15, pady=(15, 10))

        frame_content = tk.Frame(
            parent, bg=COLORS['bg_secondary'],
            relief='flat', borderwidth=1,
            highlightthickness=1, highlightbackground=COLORS['border_light'],
        )
        frame_content.pack(fill='both', expand=True, padx=15, pady=(0, 15))

        scrollbar_adm = ttk.Scrollbar(frame_content)
        scrollbar_adm.pack(side='right', fill='y')

        listbox_adm = tk.Listbox(
            frame_content, yscrollcommand=scrollbar_adm.set,
            height=20, font=FONTS['mono'],
            bg=COLORS['bg_secondary'], fg=COLORS['text_primary'],
            selectbackground=COLORS['primary'], selectforeground='white',
            borderwidth=0,
        )
        listbox_adm.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar_adm.config(command=listbox_adm.yview)

        produtos_dados_adm = self.app.db.executar_query("""
            SELECT p.*,
                   AVG(a.estrelas) AS media_avaliacao,
                   COUNT(a.id_avaliacao) AS num_avaliacoes
            FROM produtos p
            LEFT JOIN avaliacoes a ON a.id_produto = p.id_produto
            GROUP BY p.id_produto
            ORDER BY p.id_produto
        """)
        produtos_adm = [Produto.from_dict(p) for p in produtos_dados_adm] if produtos_dados_adm else []

        listbox_adm.insert('end', f"  {'ID':<5} │ {'Nome':<28} │ {'Preço':>8} │ {'Stock':>5} │ Avaliação")
        listbox_adm.insert('end', '  ' + '─' * 70)

        if produtos_dados_adm:
            for p_data in produtos_dados_adm:
                media = p_data.get('media_avaliacao')
                if media is not None:
                    media = float(media)
                    stars = '★' * round(media) + '☆' * (5 - round(media))
                    rating_str = f"{stars} {media:.1f}"
                else:
                    rating_str = '☆☆☆☆☆'
                listbox_adm.insert(
                    'end',
                    f"  {p_data['id_produto']:<5} │ {str(p_data['nome'])[:26]:<28} │ "
                    f"€{float(p_data['preco']):>7.2f} │ {p_data['stock']:>5} │ {rating_str}",
                )

        frame_botoes = tk.Frame(parent, bg=COLORS['bg'])
        frame_botoes.pack(fill='x', padx=15, pady=(0, 15))

        def ver_detalhes_adm():
            sel = listbox_adm.curselection()
            # índices 0 e 1 são cabeçalho e separador
            if not sel or sel[0] < 2:
                self.app.notify.warning("Selecione um produto para ver os detalhes!")
                return
            idx = sel[0] - 2
            if idx >= len(produtos_adm):
                return
            produto = produtos_adm[idx]
            p_data = produtos_dados_adm[idx]
            media = p_data.get('media_avaliacao')
            num = p_data.get('num_avaliacoes', 0)
            self.app._mostrar_detalhes_produto(
                produto,
                float(media) if media is not None else None,
                int(num),
            )

        tk.Button(
            frame_botoes, text="➕ Novo Produto",
            command=lambda: self._janela_novo_produto(parent),
            font=FONTS['normal'], bg=COLORS['success'], fg='white',
            relief='flat', padx=20, pady=10, cursor='hand2',
            activebackground='#059669',
        ).pack(side='left', padx=5)

        tk.Button(
            frame_botoes, text="👁️ Ver Detalhes",
            command=ver_detalhes_adm, font=FONTS['normal'],
            bg=COLORS['info'], fg='white', relief='flat',
            padx=20, pady=10, cursor='hand2', activebackground='#0891b2',
        ).pack(side='left', padx=5)

        tk.Button(
            frame_botoes, text="🔄 Recarregar",
            command=lambda: self._criar_aba_gerir_produtos(parent),
            font=FONTS['normal'], bg=COLORS['primary'], fg='white',
            relief='flat', padx=20, pady=10, cursor='hand2',
            activebackground='#1d4ed8',
        ).pack(side='left', padx=5)

    def _janela_novo_produto(self, parent):
        """Abre janela para adicionar novo produto."""
        janela = tk.Toplevel(self.master)
        janela.title("➕ Novo Produto")
        janela.geometry("550x520")
        janela.configure(bg=COLORS['bg'])

        frame_main = tk.Frame(janela, bg=COLORS['bg'])
        frame_main.pack(fill='both', expand=True, padx=20, pady=20)

        tk.Label(
            frame_main, text="➕ Adicionar Novo Produto",
            font=FONTS['subtitle'], fg=COLORS['primary'], bg=COLORS['bg'],
        ).pack(pady=(0, 20))

        tk.Label(
            frame_main, text="📝 Nome do Produto *",
            font=FONTS['normal'], fg=COLORS['text_primary'], bg=COLORS['bg'],
        ).pack(anchor='w', pady=(10, 5))
        entry_nome = ttk.Entry(frame_main, width=50, font=FONTS['normal'])
        entry_nome.pack(fill='x', pady=(0, 15))
        entry_nome.focus()

        tk.Label(
            frame_main, text="📄 Descrição",
            font=FONTS['normal'], fg=COLORS['text_primary'], bg=COLORS['bg'],
        ).pack(anchor='w', pady=(10, 5))
        text_descricao = tk.Text(
            frame_main, height=4, width=50, font=FONTS['small'],
            bg=COLORS['bg_secondary'], fg=COLORS['text_primary'],
        )
        text_descricao.pack(fill='x', pady=(0, 15))

        frame_preco_stock = tk.Frame(frame_main, bg=COLORS['bg'])
        frame_preco_stock.pack(fill='x', pady=(10, 15))

        tk.Label(
            frame_preco_stock, text="💵 Preço (€) *",
            font=FONTS['normal'], fg=COLORS['text_primary'], bg=COLORS['bg'],
        ).pack(side='left', padx=(0, 15))
        entry_preco = ttk.Entry(frame_preco_stock, width=15, font=FONTS['normal'])
        entry_preco.pack(side='left')

        tk.Label(
            frame_preco_stock, text="📦 Stock *",
            font=FONTS['normal'], fg=COLORS['text_primary'], bg=COLORS['bg'],
        ).pack(side='left', padx=(40, 15))
        entry_stock = ttk.Entry(frame_preco_stock, width=15, font=FONTS['normal'])
        entry_stock.pack(side='left')

        label_status = tk.Label(
            frame_main, text="", foreground=COLORS['danger'],
            bg=COLORS['bg'], font=FONTS['normal'],
        )
        label_status.pack(anchor='w', pady=10)

        frame_botoes_form = tk.Frame(frame_main, bg=COLORS['bg'])
        frame_botoes_form.pack(fill='x', pady=20)

        def validar_e_guardar():
            nome = entry_nome.get().strip()
            descricao = text_descricao.get("1.0", 'end-1c').strip()
            preco_str = entry_preco.get().strip()
            stock_str = entry_stock.get().strip()

            valido, msg = validar_nome_produto(nome)
            if not valido:
                label_status.config(text=f"⚠️  {msg}", foreground=COLORS['danger'])
                entry_nome.focus()
                return

            valido, preco, msg = validar_preco(preco_str)
            if not valido:
                label_status.config(text=f"⚠️  {msg}", foreground=COLORS['danger'])
                entry_preco.focus()
                return

            valido, stock, msg = validar_stock(stock_str)
            if not valido:
                label_status.config(text=f"⚠️  {msg}", foreground=COLORS['danger'])
                entry_stock.focus()
                return

            resultado = self.app.db.executar_update(
                "INSERT INTO produtos (nome, descricao, preco, stock) VALUES (%s, %s, %s, %s)",
                (nome, descricao or None, preco, stock),
            )
            if resultado:
                label_status.config(
                    text=f"✅ Produto '{nome}' adicionado com sucesso!",
                    foreground=COLORS['success'],
                )
                self.master.after(1500, lambda: janela.destroy())
                self._criar_aba_gerir_produtos(parent)
            else:
                label_status.config(
                    text="❌ Erro ao adicionar produto!",
                    foreground=COLORS['danger'],
                )

        tk.Button(
            frame_botoes_form, text="✅ Guardar",
            command=validar_e_guardar, font=FONTS['normal'],
            bg=COLORS['success'], fg='white', relief='flat',
            padx=30, pady=10, cursor='hand2', activebackground='#059669',
        ).pack(side='left', padx=5, fill='x', expand=True)

        tk.Button(
            frame_botoes_form, text="❌ Cancelar",
            command=janela.destroy, font=FONTS['normal'],
            bg=COLORS['danger'], fg='white', relief='flat',
            padx=30, pady=10, cursor='hand2', activebackground='#dc2626',
        ).pack(side='left', padx=5, fill='x', expand=True)

        janela.bind('<Return>', lambda e: validar_e_guardar())

    # ------------------------------------------------------------------ #
    #  Aba 2 — Gerir Clientes                                              #
    # ------------------------------------------------------------------ #

    def _criar_aba_gerir_clientes(self, parent):
        for widget in parent.winfo_children():
            widget.destroy()

        tk.Label(
            parent, text="Lista de Clientes",
            font=FONTS['subtitle'], fg=COLORS['primary'], bg=COLORS['bg'],
        ).pack(anchor='w', padx=15, pady=(15, 10))

        frame_content = tk.Frame(
            parent, bg=COLORS['bg_secondary'],
            relief='flat', borderwidth=1,
            highlightthickness=1, highlightbackground=COLORS['border_light'],
        )
        frame_content.pack(fill='both', expand=True, padx=15, pady=(0, 15))

        text = tk.Text(
            frame_content, height=20, width=100, font=FONTS['mono'],
            bg=COLORS['bg_secondary'], fg=COLORS['text_primary'],
            relief='flat', borderwidth=0,
        )
        text.pack(fill='both', expand=True, padx=15, pady=15)

        clientes_dados = self.app.db.executar_query(
            "SELECT id_cliente, nome, email, is_admin FROM clientes ORDER BY id_cliente"
        )
        clientes = [Cliente.from_dict(c) for c in clientes_dados] if clientes_dados else []

        text.insert('end', f"  {'ID':<5} │ {'Nome':<25} │ {'Email':<35} │ {'Admin':<10}\n")
        text.insert('end', "  " + "=" * 82 + "\n")

        for c in clientes:
            admin = "👨‍💼 Sim" if c.is_admin else "👤 Não"
            text.insert(
                'end',
                f"  {c.id_cliente:<5} │ {c.nome[:23]:<25} │ {c.email:<35} │ {admin:<10}\n",
            )

        text.config(state='disabled')

        frame_botoes = tk.Frame(parent, bg=COLORS['bg'])
        frame_botoes.pack(fill='x', padx=15, pady=(0, 15))

        tk.Button(
            frame_botoes, text="🔄 Recarregar",
            command=lambda: self._criar_aba_gerir_clientes(parent),
            font=FONTS['normal'], bg=COLORS['info'], fg='white',
            relief='flat', padx=20, pady=10, cursor='hand2',
            activebackground='#0891b2',
        ).pack(side='left', padx=5)

    # ------------------------------------------------------------------ #
    #  Aba 3 — Ver Vendas                                                  #
    # ------------------------------------------------------------------ #

    def _criar_aba_vendas(self, parent):
        for widget in parent.winfo_children():
            widget.destroy()

        tk.Label(
            parent, text="Histórico de Vendas",
            font=FONTS['subtitle'], fg=COLORS['primary'], bg=COLORS['bg'],
        ).pack(anchor='w', padx=15, pady=(15, 10))

        frame_content = tk.Frame(
            parent, bg=COLORS['bg_secondary'],
            relief='flat', borderwidth=1,
            highlightthickness=1, highlightbackground=COLORS['border_light'],
        )
        frame_content.pack(fill='both', expand=True, padx=15, pady=(0, 15))

        text = tk.Text(
            frame_content, height=20, width=100, font=FONTS['mono'],
            bg=COLORS['bg_secondary'], fg=COLORS['text_primary'],
            relief='flat', borderwidth=0,
        )
        text.pack(fill='both', expand=True, padx=15, pady=15)

        vendas = self.app.db.executar_query("""
            SELECT v.id_venda, c.nome, v.data, v.total
            FROM vendas v
            JOIN clientes c ON v.id_cliente = c.id_cliente
            ORDER BY v.data DESC
            LIMIT 50
        """)

        text.insert('end', f"  {'ID':<8} │ {'Cliente':<25} │ {'Data':<15} │ {'Total':<15}\n")
        text.insert('end', "  " + "=" * 72 + "\n")

        if vendas:
            for v in vendas:
                text.insert(
                    'end',
                    f"  {v['id_venda']:<8} │ {v['nome'][:23]:<25} │"
                    f" {str(v['data']):<15} │ €{v['total']:>12.2f}\n",
                )

        text.config(state='disabled')

        frame_botoes = tk.Frame(parent, bg=COLORS['bg'])
        frame_botoes.pack(fill='x', padx=15, pady=(0, 15))

        tk.Button(
            frame_botoes, text="🔄 Recarregar",
            command=lambda: self._criar_aba_vendas(parent),
            font=FONTS['normal'], bg=COLORS['info'], fg='white',
            relief='flat', padx=20, pady=10, cursor='hand2',
            activebackground='#0891b2',
        ).pack(side='left', padx=5)
