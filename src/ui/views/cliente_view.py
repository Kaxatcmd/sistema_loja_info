"""
Vista do Cliente
Abas de exploração de produtos, carrinho e avaliações.
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime

from src.config import FONTS, COLORS
from src.models.produto import Produto
from src.ui.components.widgets import criar_header_executivo


class ClienteView:
    """Interface em abas para o cliente autenticado."""

    def __init__(self, master, app):
        """
        Args:
            master: Janela raiz Tkinter.
            app:    Instância de LojaApp — fornece db, usuario_atual, notify, carrinho.
        """
        self.master = master
        self.app = app
        self.text_carrinho = None
        self._frame_explorar_produtos = None
        self._frame_avaliacoes = None

    # ------------------------------------------------------------------ #
    #  Ponto de entrada                                                    #
    # ------------------------------------------------------------------ #

    def criar_interface(self):
        """Monta o header e o notebook com as três abas do cliente."""
        criar_header_executivo(
            self.master,
            titulo=f"👤 Bem-vindo, {self.app.usuario_atual.nome}!",
            usuario=self.app.usuario_atual.email,
            callback_logout=self.app.fazer_logout,
        )

        notebook = ttk.Notebook(self.master)
        notebook.pack(fill='both', expand=True, padx=15, pady=15)

        frame_produtos = ttk.Frame(notebook)
        notebook.add(frame_produtos, text="🛍️ Explorar Produtos")
        self._frame_explorar_produtos = frame_produtos
        self._criar_aba_explorar_produtos(frame_produtos)

        frame_carrinho = ttk.Frame(notebook)
        notebook.add(frame_carrinho, text="🛒 Meu Carrinho")
        self._criar_aba_carrinho(frame_carrinho)

        frame_avaliacoes = ttk.Frame(notebook)
        notebook.add(frame_avaliacoes, text="⭐ Minhas Avaliações")
        self._frame_avaliacoes = frame_avaliacoes
        self._criar_aba_avaliacoes(frame_avaliacoes)

    # ------------------------------------------------------------------ #
    #  Aba 1 — Explorar Produtos                                           #
    # ------------------------------------------------------------------ #

    def _criar_aba_explorar_produtos(self, parent):
        for widget in parent.winfo_children():
            widget.destroy()

        frame_lista = ttk.Frame(parent)
        frame_lista.pack(fill='both', expand=True, padx=15, pady=15)

        tk.Label(
            frame_lista, text="Produtos Disponíveis",
            font=FONTS['subtitle'], fg=COLORS['primary'], bg=COLORS['bg'],
        ).pack(anchor='w', pady=(0, 10))

        container = tk.Frame(
            frame_lista, bg=COLORS['bg_secondary'],
            relief='flat', borderwidth=1,
            highlightthickness=1, highlightbackground=COLORS['border_light'],
        )
        container.pack(fill='both', expand=True)

        scrollbar = ttk.Scrollbar(container)
        scrollbar.pack(side='right', fill='y')

        listbox = tk.Listbox(
            container, yscrollcommand=scrollbar.set,
            height=20, font=FONTS['small'],
            bg=COLORS['bg_secondary'], fg=COLORS['text_primary'],
            selectbackground=COLORS['primary'], selectforeground='white',
            borderwidth=0,
        )
        listbox.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.config(command=listbox.yview)

        produtos_dados = self.app.db.executar_query("""
            SELECT p.*,
                   AVG(a.estrelas) as media_avaliacao,
                   COUNT(a.id_avaliacao) as num_avaliacoes
            FROM produtos p
            LEFT JOIN avaliacoes a ON a.id_produto = p.id_produto
            WHERE p.stock > 0
            GROUP BY p.id_produto
            ORDER BY p.nome
        """)

        produtos = [Produto.from_dict(p) for p in produtos_dados] if produtos_dados else []

        if not produtos:
            listbox.insert('end', "   Nenhum produto disponível no momento")
        else:
            for p_data in produtos_dados:
                media = p_data.get('media_avaliacao')
                if media is not None:
                    media = float(media)
                    filled = round(media)
                    rating_str = f"  │  {'★' * filled + '☆' * (5 - filled)} {media:.1f}"
                else:
                    rating_str = "  │  ☆☆☆☆☆"
                listbox.insert(
                    'end',
                    f"  {p_data['nome']:<35} € {float(p_data['preco']):>8.2f}"
                    f"  │  Stock: {p_data['stock']}{rating_str}",
                )

        def adicionar():
            sel = listbox.curselection()
            if not sel:
                self.app.notify.warning("Selecione um produto!")
                return
            if not produtos:
                return
            produto = produtos[sel[0]]
            self.app.carrinho.append(produto)
            self.app.notify.success(f"'{produto.nome}' adicionado ao carrinho!")
            self._atualizar_aba_carrinho()

        def ver_detalhes():
            sel = listbox.curselection()
            if not sel:
                self.app.notify.warning("Selecione um produto para ver os detalhes!")
                return
            if not produtos:
                return
            produto = produtos[sel[0]]
            p_data = produtos_dados[sel[0]]
            media = p_data.get('media_avaliacao')
            num = p_data.get('num_avaliacoes', 0)
            self.app._mostrar_detalhes_produto(
                produto,
                float(media) if media is not None else None,
                int(num),
            )

        frame_botoes = ttk.Frame(parent)
        frame_botoes.pack(fill='x', padx=15, pady=10)

        tk.Button(
            frame_botoes, text="🛒 Adicionar ao Carrinho",
            command=adicionar, font=FONTS['normal'],
            bg=COLORS['success'], fg='white', relief='flat',
            padx=20, pady=10, cursor='hand2', activebackground='#059669',
        ).pack(side='left', padx=5)

        tk.Button(
            frame_botoes, text="👁️ Ver Detalhes",
            command=ver_detalhes, font=FONTS['normal'],
            bg=COLORS['info'], fg='white', relief='flat',
            padx=20, pady=10, cursor='hand2', activebackground='#0891b2',
        ).pack(side='left', padx=5)

    # ------------------------------------------------------------------ #
    #  Aba 2 — Carrinho                                                    #
    # ------------------------------------------------------------------ #

    def _criar_aba_carrinho(self, parent):
        tk.Label(
            parent, text="Itens no Carrinho",
            font=FONTS['subtitle'], fg=COLORS['primary'], bg=COLORS['bg'],
        ).pack(anchor='w', padx=15, pady=(15, 10))

        frame_info = tk.Frame(
            parent, bg=COLORS['bg_secondary'],
            relief='flat', borderwidth=1,
            highlightthickness=1, highlightbackground=COLORS['border_light'],
        )
        frame_info.pack(fill='both', expand=True, padx=15, pady=(0, 15))

        self.text_carrinho = tk.Text(
            frame_info, height=15, width=80,
            font=FONTS['mono'], bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary'], relief='flat', borderwidth=0,
        )
        self.text_carrinho.pack(fill='both', expand=True, padx=15, pady=15)

        self._atualizar_aba_carrinho()

        frame_botoes = tk.Frame(parent, bg=COLORS['bg'])
        frame_botoes.pack(fill='x', padx=15, pady=(0, 15))

        def finalizar_compra():
            if not self.app.carrinho:
                self.app.notify.warning("Carrinho vazio!")
                return

            total = sum(item.preco for item in self.app.carrinho)
            nomes = ", ".join(item.nome for item in self.app.carrinho)

            def confirmar_compra(resposta):
                if resposta:
                    id_venda = self.app.db.executar_update(
                        "INSERT INTO vendas (id_cliente, data, total) VALUES (%s, %s, %s)",
                        (self.app.usuario_atual.id_cliente, datetime.now().date(), total),
                    )
                    if id_venda:
                        for item in self.app.carrinho:
                            self.app.db.executar_update(
                                "INSERT INTO venda_produto"
                                " (id_venda, id_produto, preco, quantidade) VALUES (%s, %s, %s, %s)",
                                (id_venda, item.id_produto, item.preco, 1),
                            )
                            self.app.db.executar_update(
                                "UPDATE produtos SET stock = stock - 1 WHERE id_produto = %s",
                                (item.id_produto,),
                            )
                        self.app.carrinho = []
                        self.app.notify.success(
                            f"Compra efetuada com sucesso! Total: €{total:.2f}"
                        )
                        self._atualizar_aba_carrinho()
                        if self._frame_avaliacoes:
                            self._criar_aba_avaliacoes(self._frame_avaliacoes)

            self.app.notify.question(
                f"Finalizar compra?\n\nTotal: €{total:.2f}",
                "Confirmar Compra",
                callback=confirmar_compra,
            )

        def limpar_carrinho():
            if self.app.carrinho:
                def confirmar_limpeza(resposta):
                    if resposta:
                        self.app.carrinho = []
                        self._atualizar_aba_carrinho()
                        self.app.notify.success("Carrinho limpo com sucesso!")

                self.app.notify.question(
                    "Tem a certeza que quer limpar o carrinho?",
                    "Limpar Carrinho",
                    callback=confirmar_limpeza,
                )

        tk.Button(
            frame_botoes, text="✅ Finalizar Compra",
            command=finalizar_compra, font=FONTS['normal'],
            bg=COLORS['success'], fg='white', relief='flat',
            padx=20, pady=10, cursor='hand2', activebackground='#059669',
        ).pack(side='left', padx=5)

        tk.Button(
            frame_botoes, text="🗑️  Limpar Carrinho",
            command=limpar_carrinho, font=FONTS['normal'],
            bg=COLORS['danger'], fg='white', relief='flat',
            padx=20, pady=10, cursor='hand2', activebackground='#dc2626',
        ).pack(side='left', padx=5)

    def _atualizar_aba_carrinho(self):
        """Atualiza o conteúdo da aba de carrinho."""
        if self.text_carrinho is None:
            return
        self.text_carrinho.config(state='normal')
        self.text_carrinho.delete(1.0, 'end')

        if not self.app.carrinho:
            self.text_carrinho.insert('end', """  
  🛒 Seu carrinho está vazio
  
  Explore produtos e adicione à sua lista de compras!
  """)
        else:
            self.text_carrinho.insert('end', "  ITENS NO CARRINHO:\n")
            self.text_carrinho.insert('end', "  " + "=" * 70 + "\n\n")
            total = 0
            for idx, item in enumerate(self.app.carrinho, 1):
                self.text_carrinho.insert(
                    'end', f"  {idx}. {item.nome:<40} €{item.preco:>10.2f}\n"
                )
                total += item.preco
            self.text_carrinho.insert('end', "\n  " + "=" * 70 + "\n")
            self.text_carrinho.insert('end', f"  TOTAL A PAGAR:  €{total:>50.2f}\n")

        self.text_carrinho.config(state='disabled')

    # ------------------------------------------------------------------ #
    #  Aba 3 — Avaliações                                                  #
    # ------------------------------------------------------------------ #

    def _criar_aba_avaliacoes(self, parent):
        for widget in parent.winfo_children():
            widget.destroy()

        tk.Label(
            parent, text="Avaliar Produtos Comprados",
            font=FONTS['subtitle'], fg=COLORS['primary'], bg=COLORS['bg'],
        ).pack(anchor='w', padx=15, pady=(15, 5))

        tk.Label(
            parent,
            text="Produtos que adquiriu — clique em ⭐ Avaliar para deixar a sua nota",
            font=FONTS['small'], fg=COLORS['text_secondary'], bg=COLORS['bg'],
        ).pack(anchor='w', padx=15, pady=(0, 10))

        dados = self.app.db.executar_query("""
            SELECT DISTINCT p.id_produto, p.nome, p.descricao, p.preco,
                   a.estrelas AS minha_avaliacao
            FROM venda_produto vp
            JOIN vendas v ON vp.id_venda = v.id_venda
            JOIN produtos p ON vp.id_produto = p.id_produto
            LEFT JOIN avaliacoes a
                   ON a.id_produto = p.id_produto AND a.id_cliente = %s
            WHERE v.id_cliente = %s
            ORDER BY p.nome
        """, (self.app.usuario_atual.id_cliente, self.app.usuario_atual.id_cliente))

        if not dados:
            tk.Label(
                parent, text="Ainda não efetuou nenhuma compra.",
                font=FONTS['normal'], fg=COLORS['text_secondary'], bg=COLORS['bg'],
            ).pack(pady=40)
            return

        outer = tk.Frame(parent, bg=COLORS['bg'])
        outer.pack(fill='both', expand=True, padx=15, pady=(0, 15))

        canvas = tk.Canvas(outer, bg=COLORS['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient='vertical', command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=COLORS['bg'])

        scrollable.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all')),
        )
        canvas.create_window((0, 0), window=scrollable, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        for item in dados:
            card = tk.Frame(
                scrollable, bg=COLORS['bg_secondary'],
                relief='flat', highlightthickness=1,
                highlightbackground=COLORS['border_light'],
            )
            card.pack(fill='x', pady=4, padx=2)

            tk.Label(
                card, text=item['nome'], font=FONTS['large'],
                fg=COLORS['text_primary'], bg=COLORS['bg_secondary'],
            ).pack(anchor='w', padx=12, pady=(10, 0))

            frame_linha = tk.Frame(card, bg=COLORS['bg_secondary'])
            frame_linha.pack(anchor='w', padx=12, pady=(4, 10))

            minha_nota = item['minha_avaliacao']
            if minha_nota:
                stars = '★' * minha_nota + '☆' * (5 - minha_nota)
                tk.Label(
                    frame_linha, text=f"A sua avaliação: {stars}",
                    font=FONTS['normal'], fg='#d97706', bg=COLORS['bg_secondary'],
                ).pack(side='left')
                btn_text = "✏️ Alterar"
            else:
                tk.Label(
                    frame_linha, text="Ainda não avaliou este produto",
                    font=FONTS['normal'], fg=COLORS['text_secondary'],
                    bg=COLORS['bg_secondary'],
                ).pack(side='left')
                btn_text = "⭐ Avaliar"

            tk.Button(
                frame_linha, text=btn_text,
                command=lambda i=item: self._mostrar_janela_avaliar(i, parent),
                font=FONTS['small'], bg=COLORS['primary'], fg='white',
                relief='flat', padx=10, pady=4, cursor='hand2',
                activebackground='#1d4ed8',
            ).pack(side='left', padx=10)

    def _mostrar_janela_avaliar(self, produto_info, parent_aba):
        """Abre popup de seleção de estrelas para avaliar o produto."""
        janela = tk.Toplevel(self.master)
        janela.title(f"⭐ Avaliar — {produto_info['nome']}")
        janela.geometry("420x300")
        janela.configure(bg=COLORS['bg'])
        janela.resizable(False, False)
        janela.grab_set()

        tk.Label(
            janela, text="Avaliar produto:",
            font=FONTS['normal'], fg=COLORS['text_secondary'], bg=COLORS['bg'],
        ).pack(pady=(20, 4))
        tk.Label(
            janela, text=produto_info['nome'],
            font=FONTS['subtitle'], fg=COLORS['primary'], bg=COLORS['bg'],
        ).pack(pady=(0, 15))
        tk.Label(
            janela, text="Selecione a sua nota:",
            font=FONTS['normal'], fg=COLORS['text_primary'], bg=COLORS['bg'],
        ).pack()

        nota_var = tk.IntVar(value=produto_info.get('minha_avaliacao') or 0)
        frame_estrelas = tk.Frame(janela, bg=COLORS['bg'])
        frame_estrelas.pack(pady=12)

        star_btns = []

        def atualizar_estrelas(valor):
            nota_var.set(valor)
            for i, b in enumerate(star_btns):
                b.config(
                    text='★' if i < valor else '☆',
                    fg='#d97706' if i < valor else COLORS['text_secondary'],
                )

        valor_inicial = produto_info.get('minha_avaliacao') or 0
        for i in range(1, 6):
            preenchido = i <= valor_inicial
            b = tk.Button(
                frame_estrelas,
                text='★' if preenchido else '☆',
                font=('Segoe UI', 26),
                fg='#d97706' if preenchido else COLORS['text_secondary'],
                bg=COLORS['bg'], relief='flat', cursor='hand2',
                activebackground=COLORS['bg'],
                command=lambda v=i: atualizar_estrelas(v),
            )
            b.pack(side='left', padx=2)
            star_btns.append(b)

        lbl_status = tk.Label(
            janela, text="", font=FONTS['small'],
            fg=COLORS['danger'], bg=COLORS['bg'],
        )
        lbl_status.pack(pady=2)

        def guardar():
            nota = nota_var.get()
            if nota == 0:
                lbl_status.config(text="⚠️  Selecione pelo menos 1 estrela!")
                return

            existente = self.app.db.executar_query(
                "SELECT id_avaliacao FROM avaliacoes"
                " WHERE id_cliente = %s AND id_produto = %s",
                (self.app.usuario_atual.id_cliente, produto_info['id_produto']),
            )
            if existente:
                self.app.db.executar_update(
                    "UPDATE avaliacoes SET estrelas = %s"
                    " WHERE id_cliente = %s AND id_produto = %s",
                    (nota, self.app.usuario_atual.id_cliente, produto_info['id_produto']),
                )
            else:
                self.app.db.executar_update(
                    "INSERT INTO avaliacoes (id_cliente, id_produto, estrelas)"
                    " VALUES (%s, %s, %s)",
                    (self.app.usuario_atual.id_cliente, produto_info['id_produto'], nota),
                )

            palavra = 'estrela' if nota == 1 else 'estrelas'
            self.app.notify.success(f"Avaliação guardada! {'★' * nota} ({nota} {palavra})")
            janela.destroy()
            self._criar_aba_avaliacoes(parent_aba)
            if self._frame_explorar_produtos:
                self._criar_aba_explorar_produtos(self._frame_explorar_produtos)

        frame_btns = tk.Frame(janela, bg=COLORS['bg'])
        frame_btns.pack(pady=10)

        tk.Button(
            frame_btns, text="✅ Guardar", command=guardar,
            font=FONTS['normal'], bg=COLORS['success'], fg='white',
            relief='flat', padx=20, pady=8, cursor='hand2',
            activebackground='#059669',
        ).pack(side='left', padx=5)

        tk.Button(
            frame_btns, text="❌ Cancelar", command=janela.destroy,
            font=FONTS['normal'], bg=COLORS['danger'], fg='white',
            relief='flat', padx=20, pady=8, cursor='hand2',
            activebackground='#dc2626',
        ).pack(side='left', padx=5)
