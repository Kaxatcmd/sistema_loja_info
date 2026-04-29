"""
Aplicação Principal - LojaApp
Interface gráfica com abas para Cliente e Administrador - Design Profissional
"""

import tkinter as tk
from tkinter import ttk, simpledialog, filedialog
from datetime import datetime
from src.config import FONTS, COLORS, WINDOW_WIDTH, WINDOW_HEIGHT, APP_TITLE
from src.database import DatabaseManager
from src.exceptions import DatabaseError
from src.utils.logger import obter_logger

logger = obter_logger(__name__)
from src.models.cliente import Cliente
from src.models.produto import Produto
from src.models.cupao import Cupao
from src.repositories.cupao_repository import CupaoRepository
from src.repositories.categoria_repository import CategoriaRepository
from src.services.stock_service import StockService
from src.services.relatorio_service import RelatorioService
from src.utils.validators import validar_nome_produto, validar_preco, validar_stock
from src.ui.screens.login import LoginScreen
from src.ui.screens.register import RegisterScreen
from src.ui.theme import (ModernStyle, criar_botao_primario, criar_botao_secundario,
                          criar_botao_perigo, criar_botao_sucesso)
from src.ui.components.widgets import criar_header_executivo, criar_separador
from src.ui.notifications import NotificationManager


class LojaApp:
    """Aplicação Principal da Loja com Interface em Abas - Design Moderno"""
    
    def __init__(self, master):
        """
        Inicializa aplicação principal
        
        Args:
            master: Janela raiz Tkinter
        """
        self.master = master
        self.master.title(APP_TITLE)
        self.master.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.master.configure(bg=COLORS['bg'])
        
        # Configurar tema moderno
        ModernStyle.configurar_temas()
        
        # Sistema de notificações
        self.notify = NotificationManager(self.master)
        
        self.db = None
        self.usuario_atual = None
        self.carrinho = []
        self.cupao_ativo: Cupao | None = None
        self.notebook = None
        self.text_carrinho = None
        self.label_cupao_status = None
        
        # Mostrar login
        self.mostrar_login()
    
    def mostrar_login(self):
        """Exibe tela de login"""
        login = LoginScreen(self.master, self.on_login_success, self.mostrar_registo, self.notify)
        login.show()
    
    def mostrar_registo(self):
        """Exibe tela de registo"""
        register = RegisterScreen(self.master, self.on_register_success, self.mostrar_login, self.notify)
        register.show()
    
    def on_register_success(self):
        """Callback executado após registo bem-sucedido"""
        # Após registo bem-sucedido, voltar ao login
        self.mostrar_login()
    
    def on_login_success(self, usuario_cliente, db):
        """
        Callback executado após login bem-sucedido
        
        Args:
            usuario_cliente (Cliente): Objeto do utilizador autenticado
            db (DatabaseManager): Gerenciador de BD
        """
        self.usuario_atual = usuario_cliente
        self.db = db

        logger.info(
            "Sessão iniciada: %s (admin=%s)",
            usuario_cliente.email,
            bool(usuario_cliente.is_admin),
        )

        if usuario_cliente.is_admin:
            self.criar_interface_admin()
            self._verificar_alertas_stock()
        else:
            self.criar_interface_cliente()
    
    def limpar_janela(self):
        """Remove todos os widgets da janela principal (exceto notification_frame)"""
        for widget in self.master.winfo_children():
            # Não destruir o frame de notificações
            if widget != self.notify.notification_frame:
                widget.destroy()
    
    def criar_interface_cliente(self):
        """Cria interface com abas para cliente"""
        self.limpar_janela()
        self.master.configure(bg=COLORS['bg'])
        
        # Header executivo
        criar_header_executivo(self.master, 
                              titulo=f"👤 Bem-vindo, {self.usuario_atual.nome}!",
                              usuario=self.usuario_atual.email,
                              callback_logout=self.fazer_logout)
        
        # Notebook (abas)
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Aba 1: Explorar Produtos
        frame_produtos = ttk.Frame(self.notebook)
        self.notebook.add(frame_produtos, text="🛍️ Explorar Produtos")
        self._criar_aba_explorar_produtos(frame_produtos)
        
        # Aba 2: Ver Carrinho
        frame_carrinho = ttk.Frame(self.notebook)
        self.notebook.add(frame_carrinho, text="🛒 Meu Carrinho")
        self._criar_aba_carrinho(frame_carrinho)

        # Aba 3: Wishlist
        frame_wishlist = ttk.Frame(self.notebook)
        self.notebook.add(frame_wishlist, text="❤️  Wishlist")
        self._frame_wishlist = frame_wishlist
        self._criar_aba_wishlist(frame_wishlist)

        # Aba 4: Avaliações
        frame_avaliacoes = ttk.Frame(self.notebook)
        self.notebook.add(frame_avaliacoes, text="⭐ Avaliações")
        self._frame_avaliacoes = frame_avaliacoes
        self._criar_aba_avaliacoes(frame_avaliacoes)

    def _criar_aba_explorar_produtos(self, parent):
        """Cria interface da aba de explorar produtos — tabela animada com Treeview."""
        # Carregar categorias
        try:
            cats_exp = CategoriaRepository(self.db).listar_todos()
        except DatabaseError:
            cats_exp = []
        cat_nomes_exp = ['Todas as categorias'] + [c.nome for c in cats_exp]

        # Carregar todos os produtos (com categoria via LEFT JOIN)
        try:
            produtos_dados = self.db.executar_query(
                """SELECT p.*, c.nome AS nome_categoria
                   FROM produtos p
                   LEFT JOIN categorias c ON c.id_categoria = p.id_categoria
                   WHERE p.stock > 0
                   ORDER BY c.nome, p.nome"""
            )
            todos_produtos = [Produto.from_dict(p) for p in produtos_dados] if produtos_dados else []
        except DatabaseError as e:
            logger.error("Erro ao carregar produtos (explorar): %s", e)
            self.notify.error(f"Erro ao carregar produtos: {e}")
            todos_produtos = []

        # Carregar médias de avaliação (id_produto → média)
        try:
            avals = self.db.executar_query(
                "SELECT id_produto, ROUND(AVG(nota), 1) AS media, COUNT(*) AS total FROM avaliacoes GROUP BY id_produto"
            )
            _media_aval = {r['id_produto']: (float(r['media']), int(r['total'])) for r in avals} if avals else {}
        except DatabaseError:
            _media_aval = {}

        def _estrelas(id_produto: int) -> str:
            """Devolve string de estrelas Unicode com média numérica, ex: ★★★★☆ 4.2"""
            if id_produto not in _media_aval:
                return '☆☆☆☆☆'
            media, _ = _media_aval[id_produto]
            cheias = int(media)
            vazias = 5 - cheias
            return '★' * cheias + '☆' * vazias + f'  {media}'

        # ── Cabeçalho: título ──────────────────────────────────────────
        frame_topo = tk.Frame(parent, bg=COLORS['bg'])
        frame_topo.pack(fill='x', padx=15, pady=(12, 6))
        tk.Label(frame_topo, text="Produtos Disponíveis",
                 font=FONTS['subtitle'], fg=COLORS['primary'],
                 bg=COLORS['bg']).pack(side='left')
        lbl_contagem = tk.Label(frame_topo, text=f"{len(todos_produtos)} produto(s)",
                                font=FONTS['small'], fg=COLORS['text_secondary'],
                                bg=COLORS['bg'])
        lbl_contagem.pack(side='right', padx=(0, 15))

        # ── Filtros: categoria + pesquisa ──────────────────────────────
        frame_filtros = tk.Frame(parent, bg=COLORS['bg'])
        frame_filtros.pack(fill='x', padx=15, pady=(0, 4))
        tk.Label(frame_filtros, text="Categoria:", font=FONTS['small'],
                 fg=COLORS['text_secondary'], bg=COLORS['bg']).pack(side='left', padx=(0, 4))
        cat_var_exp = tk.StringVar(value='Todas as categorias')
        combo_cat_exp = ttk.Combobox(frame_filtros, textvariable=cat_var_exp,
                                      values=cat_nomes_exp, state='readonly', width=22,
                                      font=FONTS['small'])
        combo_cat_exp.pack(side='left', padx=(0, 15))
        tk.Label(frame_filtros, text="🔍", font=FONTS['normal'],
                 bg=COLORS['bg']).pack(side='left', padx=(0, 4))
        entry_pesquisa = ttk.Entry(frame_filtros, width=22, font=FONTS['normal'])
        entry_pesquisa.pack(side='left')

        # ── Container da tabela ─────────────────────────────────────────
        container = tk.Frame(parent, bg=COLORS['bg_secondary'],
                             relief='flat', borderwidth=1,
                             highlightthickness=1,
                             highlightbackground=COLORS['border_light'])
        container.pack(fill='both', expand=True, padx=15, pady=(0, 8))
        scrollbar = ttk.Scrollbar(container, orient='vertical')
        scrollbar.pack(side='right', fill='y')

        # ── Treeview ──────────────────────────────────────────────────
        colunas = ('categoria', 'nome', 'avaliacao', 'preco', 'stock', 'estado')
        tree = ttk.Treeview(container, columns=colunas, show='headings',
                            yscrollcommand=scrollbar.set,
                            selectmode='browse', height=15)
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=tree.yview)

        tree.heading('categoria',  text='Categoria',       anchor='w')
        tree.heading('nome',       text='Nome do Produto', anchor='w')
        tree.heading('avaliacao',  text='Avaliação',       anchor='center')
        tree.heading('preco',      text='Preço',           anchor='e')
        tree.heading('stock',      text='Stock',           anchor='center')
        tree.heading('estado',     text='Disponibilidade', anchor='center')

        tree.column('categoria',  width=135, anchor='w',      stretch=False)
        tree.column('nome',       width=255, anchor='w',      stretch=True)
        tree.column('avaliacao',  width=115, anchor='center', stretch=False)
        tree.column('preco',      width=90,  anchor='e',      stretch=False)
        tree.column('stock',      width=60,  anchor='center', stretch=False)
        tree.column('estado',     width=140, anchor='center', stretch=False)

        tree.tag_configure('odd',       background='#f8fafc', foreground=COLORS['text_primary'])
        tree.tag_configure('even',      background='#ffffff', foreground=COLORS['text_primary'])
        tree.tag_configure('hover',     background='#dbeafe', foreground=COLORS['primary'])
        tree.tag_configure('low_stock', foreground=COLORS['warning'])

        produtos_visiveis: list[Produto] = []

        def _popular_tabela(filtro_nome='', filtro_cat='Todas as categorias'):
            nonlocal produtos_visiveis
            tree.delete(*tree.get_children())
            fl = filtro_nome.lower()
            produtos_visiveis = [
                p for p in todos_produtos
                if (fl in p.nome.lower() or fl == '')
                and (filtro_cat == 'Todas as categorias'
                     or (p.nome_categoria or '—') == filtro_cat)
            ]
            lbl_contagem.config(text=f"{len(produtos_visiveis)} produto(s)")
            for idx, p in enumerate(produtos_visiveis):
                tag_linha = 'odd' if idx % 2 == 0 else 'even'
                if p.stock <= 3:
                    tag_linha = 'low_stock'
                disponivel = "✅ Disponível" if p.stock > 3 else (
                    "⚠️  Stock Baixo" if p.stock > 0 else "❌ Esgotado"
                )
                tree.insert('', 'end', iid=str(idx),
                            values=(p.nome_categoria or '—',
                                    f"  {p.nome}",
                                    _estrelas(p.id_produto),
                                    f"€ {p.preco:.2f}",
                                    p.stock, disponivel),
                            tags=(tag_linha,))

        _popular_tabela()

        # ── Hover ─────────────────────────────────────────────────────
        _ultima_linha: dict = {'iid': None, 'tags': ()}

        def _on_motion(event):
            iid = tree.identify_row(event.y)
            if iid == _ultima_linha['iid']:
                return
            prev = _ultima_linha['iid']
            if prev and tree.exists(prev):
                tree.item(prev, tags=_ultima_linha['tags'])
            if iid:
                orig_tags = tree.item(iid, 'tags')
                _ultima_linha['iid'] = iid
                _ultima_linha['tags'] = orig_tags
                tree.item(iid, tags=('hover',))
            else:
                _ultima_linha['iid'] = None

        def _on_leave(event):
            prev = _ultima_linha['iid']
            if prev and tree.exists(prev):
                tree.item(prev, tags=_ultima_linha['tags'])
            _ultima_linha['iid'] = None

        tree.bind('<Motion>', _on_motion)
        tree.bind('<Leave>',  _on_leave)

        def _on_filtro(*_):
            _on_leave(None)
            _popular_tabela(entry_pesquisa.get().strip(), cat_var_exp.get())

        entry_pesquisa.bind('<KeyRelease>', _on_filtro)
        combo_cat_exp.bind('<<ComboboxSelected>>', _on_filtro)

        def _produto_selecionado() -> Produto | None:
            sel = tree.selection()
            if not sel:
                self.notify.warning("Selecione um produto!")
                return None
            return produtos_visiveis[int(sel[0])]

        # ── Ações ──────────────────────────────────────────────────────
        def adicionar():
            produto = _produto_selecionado()
            if produto is None:
                return
            self.carrinho.append(produto)
            self.notify.success(f"'{produto.nome}' adicionado ao carrinho!")
            self._atualizar_aba_carrinho()

        def adicionar_wishlist():
            produto = _produto_selecionado()
            if produto is None:
                return
            try:
                existe = self.db.executar_query(
                    "SELECT id_wishlist FROM wishlist WHERE id_cliente = %s AND id_produto = %s",
                    (self.usuario_atual.id_cliente, produto.id_produto)
                )
                if existe:
                    self.notify.warning(f"'{produto.nome}' já está na wishlist!")
                    return
                self.db.executar_update(
                    "INSERT INTO wishlist (id_cliente, id_produto) VALUES (%s, %s)",
                    (self.usuario_atual.id_cliente, produto.id_produto)
                )
                self.notify.success(f"'{produto.nome}' adicionado à wishlist!")
                if hasattr(self, '_frame_wishlist'):
                    self._criar_aba_wishlist(self._frame_wishlist)
            except DatabaseError as e:
                logger.error("Erro ao adicionar wishlist: %s", e)
                self.notify.error(f"Erro: {e}")

        tree.bind('<Double-Button-1>', lambda e: adicionar())

        # ── Botões ─────────────────────────────────────────────────────
        frame_botoes = tk.Frame(parent, bg=COLORS['bg'])
        frame_botoes.pack(fill='x', padx=15, pady=(0, 12))

        btn_adicionar = tk.Button(frame_botoes, text="🛒 Adicionar ao Carrinho",
                                  command=adicionar, font=FONTS['normal'],
                                  bg=COLORS['success'], fg='white', relief='flat',
                                  padx=20, pady=10, cursor='hand2',
                                  activebackground='#059669')
        btn_adicionar.pack(side='left', padx=5)
        btn_adicionar.bind('<Enter>', lambda e: btn_adicionar.config(bg='#059669'))
        btn_adicionar.bind('<Leave>', lambda e: btn_adicionar.config(bg=COLORS['success']))

        btn_wishlist = tk.Button(frame_botoes, text="❤️  Wishlist",
                                 command=adicionar_wishlist, font=FONTS['normal'],
                                 bg='#e11d48', fg='white', relief='flat',
                                 padx=20, pady=10, cursor='hand2',
                                 activebackground='#be123c')
        btn_wishlist.pack(side='left', padx=5)
        btn_wishlist.bind('<Enter>', lambda e: btn_wishlist.config(bg='#be123c'))
        btn_wishlist.bind('<Leave>', lambda e: btn_wishlist.config(bg='#e11d48'))

    def _criar_aba_carrinho(self, parent):
        """Cria interface da aba de carrinho"""
        # Título
        titulo = tk.Label(parent, text="Itens no Carrinho",
                         font=FONTS['subtitle'], fg=COLORS['primary'],
                         bg=COLORS['bg'])
        titulo.pack(anchor='w', padx=15, pady=(15, 6))

        # Treeview para itens
        container = tk.Frame(parent, bg=COLORS['bg_secondary'], relief='flat',
                             borderwidth=1, highlightthickness=1,
                             highlightbackground=COLORS['border_light'])
        container.pack(fill='both', expand=True, padx=15, pady=(0, 4))
        sb = ttk.Scrollbar(container)
        sb.pack(side='right', fill='y')

        colunas = ('num', 'nome', 'preco')
        self.tree_carrinho = ttk.Treeview(container, columns=colunas, show='headings',
                                          yscrollcommand=sb.set, selectmode='browse', height=12)
        self.tree_carrinho.pack(side='left', fill='both', expand=True)
        sb.config(command=self.tree_carrinho.yview)

        self.tree_carrinho.heading('num',   text='#',      anchor='center')
        self.tree_carrinho.heading('nome',  text='Produto', anchor='w')
        self.tree_carrinho.heading('preco', text='Preço',  anchor='e')
        self.tree_carrinho.column('num',   width=40,  anchor='center', stretch=False)
        self.tree_carrinho.column('nome',  width=420, anchor='w',      stretch=True)
        self.tree_carrinho.column('preco', width=120, anchor='e',      stretch=False)

        self.tree_carrinho.tag_configure('odd',   background='#f8fafc')
        self.tree_carrinho.tag_configure('even',  background='#ffffff')
        self.tree_carrinho.tag_configure('hover', background='#dbeafe', foreground=COLORS['primary'])

        _hover_c: dict = {'iid': None, 'tags': ()}

        def _motion_c(e):
            iid = self.tree_carrinho.identify_row(e.y)
            if iid == _hover_c['iid']:
                return
            if _hover_c['iid'] and self.tree_carrinho.exists(_hover_c['iid']):
                self.tree_carrinho.item(_hover_c['iid'], tags=_hover_c['tags'])
            if iid:
                _hover_c['iid'] = iid
                _hover_c['tags'] = self.tree_carrinho.item(iid, 'tags')
                self.tree_carrinho.item(iid, tags=('hover',))
            else:
                _hover_c['iid'] = None

        def _leave_c(e):
            if _hover_c['iid'] and self.tree_carrinho.exists(_hover_c['iid']):
                self.tree_carrinho.item(_hover_c['iid'], tags=_hover_c['tags'])
            _hover_c['iid'] = None

        self.tree_carrinho.bind('<Motion>', _motion_c)
        self.tree_carrinho.bind('<Leave>',  _leave_c)

        # Painel de resumo (subtotal / desconto / total)
        self.frame_resumo = tk.Frame(parent, bg=COLORS['bg_secondary'],
                                     highlightthickness=1,
                                     highlightbackground=COLORS['border_light'])
        self.frame_resumo.pack(fill='x', padx=15, pady=(0, 4))

        self._atualizar_aba_carrinho()

        # --- Secção de cupão ---
        frame_cupao = tk.Frame(parent, bg=COLORS['bg'])
        frame_cupao.pack(fill='x', padx=15, pady=(0, 5))

        tk.Label(frame_cupao, text="🎟️  Cupão de desconto:",
                 font=FONTS['normal'], fg=COLORS['text_primary'],
                 bg=COLORS['bg']).pack(side='left', padx=(0, 8))

        self._entry_cupao = ttk.Entry(frame_cupao, width=18, font=FONTS['normal'])
        self._entry_cupao.pack(side='left', padx=(0, 8))

        def aplicar_cupao():
            codigo = self._entry_cupao.get().strip()
            if not codigo:
                self.label_cupao_status.config(
                    text="Introduza um código de cupão.", fg=COLORS['danger'])
                return
            repo = CupaoRepository(self.db)
            valido, cupao, msg = repo.validar_cupao(codigo)
            if valido:
                self.cupao_ativo = cupao
                desconto_fmt = (
                    f"{cupao.desconto:.0f}%"
                    if cupao.tipo == "percentagem"
                    else f"€{cupao.desconto:.2f}"
                )
                self.label_cupao_status.config(
                    text=f"✅ Cupão aplicado! Desconto: {desconto_fmt}",
                    fg=COLORS['success'])
                logger.info("Cupão aplicado: %r (desconto=%s %s)",
                            cupao.codigo, cupao.desconto, cupao.tipo)
            else:
                self.cupao_ativo = None
                self.label_cupao_status.config(text=f"❌ {msg}", fg=COLORS['danger'])
            self._atualizar_aba_carrinho()

        def remover_cupao():
            self.cupao_ativo = None
            self._entry_cupao.delete(0, 'end')
            self.label_cupao_status.config(text="", fg=COLORS['text_primary'])
            self._atualizar_aba_carrinho()

        tk.Button(frame_cupao, text="Aplicar",
                  command=aplicar_cupao,
                  font=FONTS['small'],
                  bg=COLORS['primary'], fg='white',
                  relief='flat', padx=10, pady=4,
                  cursor='hand2').pack(side='left', padx=(0, 4))

        tk.Button(frame_cupao, text="Remover",
                  command=remover_cupao,
                  font=FONTS['small'],
                  bg=COLORS['danger'], fg='white',
                  relief='flat', padx=10, pady=4,
                  cursor='hand2').pack(side='left')

        self.label_cupao_status = tk.Label(frame_cupao, text="",
                                           font=FONTS['small'],
                                           bg=COLORS['bg'],
                                           fg=COLORS['text_primary'])
        self.label_cupao_status.pack(side='left', padx=10)

        # Frame de botões
        frame_botoes = tk.Frame(parent, bg=COLORS['bg'])
        frame_botoes.pack(fill='x', padx=15, pady=(0, 15))

        def finalizar_compra():
            if not self.carrinho:
                self.notify.warning("Carrinho vazio!")
                return

            subtotal = sum(float(item.preco) for item in self.carrinho if item.preco is not None)
            desconto_valor = 0.0
            if self.cupao_ativo and self.cupao_ativo.esta_valido():
                desconto_valor = float(self.cupao_ativo.calcular_desconto(subtotal))
            total = max(0.0, subtotal - desconto_valor)

            msg_confirmacao = f"Finalizar compra?\n\nSubtotal: €{subtotal:.2f}"
            if desconto_valor > 0:
                msg_confirmacao += f"\nDesconto ({self.cupao_ativo.codigo}): -€{desconto_valor:.2f}"
            msg_confirmacao += f"\nTotal a pagar: €{total:.2f}"

            def confirmar_compra(resposta):
                if resposta:
                    try:
                        id_venda = self.db.executar_update(
                            "INSERT INTO vendas (id_cliente, data, total) VALUES (%s, %s, %s)",
                            (self.usuario_atual.id_cliente, datetime.now().date(), total)
                        )
                        for item in self.carrinho:
                            self.db.executar_update(
                                "INSERT INTO venda_produto (id_venda, id_produto, preco, quantidade) VALUES (%s, %s, %s, %s)",
                                (id_venda, item.id_produto, item.preco, 1)
                            )
                            self.db.executar_update(
                                "UPDATE produtos SET stock = stock - 1 WHERE id_produto = %s",
                                (item.id_produto,)
                            )
                        logger.info(
                            "Venda #%s criada — cliente_id=%s, subtotal=€%.2f, "
                            "desconto=€%.2f, total=€%.2f, cupao=%r, itens=%d",
                            id_venda,
                            self.usuario_atual.id_cliente,
                            subtotal,
                            desconto_valor,
                            total,
                            self.cupao_ativo.codigo if self.cupao_ativo else None,
                            len(self.carrinho),
                        )
                        self.carrinho = []
                        self.cupao_ativo = None
                        if self.label_cupao_status:
                            self.label_cupao_status.config(text="")
                        if hasattr(self, '_entry_cupao'):
                            self._entry_cupao.delete(0, 'end')
                        self.notify.success(
                            f"Compra finalizada!\nID da venda: {id_venda}\nTotal: €{total:.2f}"
                        )
                        self._atualizar_aba_carrinho()
                    except DatabaseError as e:
                        logger.error(
                            "Erro de BD ao finalizar compra (cliente_id=%s): %s",
                            self.usuario_atual.id_cliente, e
                        )
                        self.notify.error(f"Erro ao finalizar compra: {e}")

            self.notify.question(msg_confirmacao, "Confirmar Compra",
                                 callback=confirmar_compra)

        def limpar_carrinho():
            if self.carrinho:
                def confirmar_limpeza(resposta):
                    if resposta:
                        self.carrinho = []
                        self._atualizar_aba_carrinho()
                        self.notify.success("Carrinho limpo com sucesso!")

                self.notify.question("Tem a certeza que quer limpar o carrinho?",
                                    "Limpar Carrinho",
                                    callback=confirmar_limpeza)

        btn_finalizar = tk.Button(frame_botoes, text="✅ Finalizar Compra",
                                 command=finalizar_compra,
                                 font=FONTS['normal'],
                                 bg=COLORS['success'], fg='white',
                                 relief='flat', padx=20, pady=10, cursor='hand2',
                                 activebackground='#059669')
        btn_finalizar.pack(side='left', padx=5)
        btn_finalizar.bind('<Enter>', lambda e: btn_finalizar.config(bg='#059669'))
        btn_finalizar.bind('<Leave>', lambda e: btn_finalizar.config(bg=COLORS['success']))

        btn_limpar = tk.Button(frame_botoes, text="🗑️  Limpar Carrinho",
                              command=limpar_carrinho,
                              font=FONTS['normal'],
                              bg=COLORS['danger'], fg='white',
                              relief='flat', padx=20, pady=10, cursor='hand2',
                              activebackground='#dc2626')
        btn_limpar.pack(side='left', padx=5)

    def _atualizar_aba_carrinho(self):
        """Atualiza o conteúdo da aba de carrinho (Treeview + resumo)."""
        if not hasattr(self, 'tree_carrinho') or self.tree_carrinho is None:
            return

        tree = self.tree_carrinho
        tree.delete(*tree.get_children())

        # Limpar painel de resumo
        if hasattr(self, 'frame_resumo') and self.frame_resumo:
            for w in self.frame_resumo.winfo_children():
                w.destroy()

        if not self.carrinho:
            tree.insert('', 'end', values=('', '  🛒  Carrinho vazio — explore produtos e adicione aqui!', ''),
                        tags=('odd',))
        else:
            subtotal = 0.0
            for idx, item in enumerate(self.carrinho, 1):
                preco = float(item.preco) if item.preco is not None else 0.0
                tag = 'odd' if idx % 2 == 1 else 'even'
                tree.insert('', 'end', iid=str(idx - 1),
                            values=(idx, f"  {item.nome}", f"€ {preco:.2f}"),
                            tags=(tag,))
                subtotal += preco

            # Painel de resumo
            desconto_val = 0.0
            if self.cupao_ativo and self.cupao_ativo.esta_valido():
                desconto_val = float(self.cupao_ativo.calcular_desconto(subtotal))
            total = max(0.0, subtotal - desconto_val)

            fr = self.frame_resumo
            fr_inner = tk.Frame(fr, bg=COLORS['bg_secondary'])
            fr_inner.pack(anchor='e', padx=15, pady=6)

            tk.Label(fr_inner, text=f"Subtotal:  € {subtotal:.2f}",
                     font=FONTS['normal'], fg=COLORS['text_primary'],
                     bg=COLORS['bg_secondary']).pack(anchor='e')
            if desconto_val > 0:
                desconto_fmt = (
                    f"{self.cupao_ativo.desconto:.0f}%"
                    if self.cupao_ativo.tipo == "percentagem"
                    else f"€{self.cupao_ativo.desconto:.2f}"
                )
                tk.Label(fr_inner,
                         text=f"Desconto ({self.cupao_ativo.codigo}, {desconto_fmt}):  -€ {desconto_val:.2f}",
                         font=FONTS['normal'], fg=COLORS['danger'],
                         bg=COLORS['bg_secondary']).pack(anchor='e')
            tk.Label(fr_inner, text=f"TOTAL:  € {total:.2f}",
                     font=FONTS['subtitle'],
                     fg=COLORS['primary'], bg=COLORS['bg_secondary']).pack(anchor='e')
    
    def criar_interface_admin(self):
        """Cria interface com abas para administrador"""
        self.limpar_janela()
        self.master.configure(bg=COLORS['bg'])
        
        # Header executivo
        criar_header_executivo(self.master, 
                              titulo=f"👨‍💼 Painel Administrativo - {self.usuario_atual.nome}",
                              usuario="Modo Administrador",
                              callback_logout=self.fazer_logout)
        
        # Notebook (abas)
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Aba 1: Gerir Produtos
        frame_produtos = ttk.Frame(self.notebook)
        self.notebook.add(frame_produtos, text="📦 Gerir Produtos")
        self._criar_aba_gerir_produtos(frame_produtos)
        
        # Aba 2: Gerir Clientes
        frame_clientes = ttk.Frame(self.notebook)
        self.notebook.add(frame_clientes, text="👥 Gerir Clientes")
        self._criar_aba_gerir_clientes(frame_clientes)
        
        # Aba 3: Ver Vendas
        frame_vendas = ttk.Frame(self.notebook)
        self.notebook.add(frame_vendas, text="📊 Ver Vendas")
        self._criar_aba_vendas(frame_vendas)

        # Aba 4: Gerir Cupões
        frame_cupoes = ttk.Frame(self.notebook)
        self.notebook.add(frame_cupoes, text="🎟️ Gerir Cupões")
        self._criar_aba_gerir_cupoes(frame_cupoes)

        # Aba 5: Gerir Categorias
        frame_cats = ttk.Frame(self.notebook)
        self.notebook.add(frame_cats, text="🗂️ Gerir Categorias")
        self._criar_aba_gerir_categorias(frame_cats)
    
    def _verificar_alertas_stock(self):
        """Emite uma notificação de aviso se houver produtos com stock baixo."""
        try:
            servico = StockService(self.db)
            resumo = servico.resumo()
            if resumo:
                self.notify.warning(f"📦 Stock baixo: {resumo}")
                logger.warning("Alerta de stock baixo: %s", resumo)
        except DatabaseError as e:
            logger.error("Erro ao verificar stock baixo: %s", e)

    def _criar_aba_gerir_produtos(self, parent):
        """Cria aba para gerir produtos — tabela com categoria."""
        for widget in parent.winfo_children():
            widget.destroy()

        # Carregar categorias (para filtro e diálogos)
        try:
            cats = CategoriaRepository(self.db).listar_todos()
        except DatabaseError:
            cats = []
        cat_map = {c.id_categoria: c.nome for c in cats}  # id → nome
        cat_nomes = ['Todas as categorias'] + [c.nome for c in cats]

        # Carregar produtos
        try:
            produtos_dados = self.db.executar_query("""
                SELECT p.*, c.nome AS nome_categoria
                FROM produtos p
                LEFT JOIN categorias c ON c.id_categoria = p.id_categoria
                ORDER BY c.nome, p.nome
            """)
            todos_produtos = [Produto.from_dict(p) for p in produtos_dados] if produtos_dados else []
        except DatabaseError as e:
            logger.error("Erro ao carregar lista de produtos (admin): %s", e)
            self.notify.error(f"Erro ao carregar produtos: {e}")
            todos_produtos = []

        # Carregar médias de avaliação (id_produto → média)
        try:
            avals = self.db.executar_query(
                "SELECT id_produto, ROUND(AVG(nota), 1) AS media FROM avaliacoes GROUP BY id_produto"
            )
            _media_aval = {r['id_produto']: float(r['media']) for r in avals} if avals else {}
        except DatabaseError:
            _media_aval = {}

        def _estrelas(id_produto: int) -> str:
            if id_produto not in _media_aval:
                return '☆☆☆☆☆'
            media = _media_aval[id_produto]
            cheias = int(media)
            return '★' * cheias + '☆' * (5 - cheias) + f'  {media}'

        # ── Cabeçalho ──────────────────────────────────────────────────
        frame_topo = tk.Frame(parent, bg=COLORS['bg'])
        frame_topo.pack(fill='x', padx=15, pady=(12, 6))

        tk.Label(frame_topo, text="Lista de Produtos",
                 font=FONTS['subtitle'], fg=COLORS['primary'],
                 bg=COLORS['bg']).pack(side='left')
        lbl_cont = tk.Label(frame_topo, text=f"{len(todos_produtos)} produto(s)",
                            font=FONTS['small'], fg=COLORS['text_secondary'],
                            bg=COLORS['bg'])
        lbl_cont.pack(side='right', padx=(0, 12))

        # Filtro de categoria
        frame_filtros = tk.Frame(parent, bg=COLORS['bg'])
        frame_filtros.pack(fill='x', padx=15, pady=(0, 4))
        tk.Label(frame_filtros, text="Categoria:", font=FONTS['small'],
                 fg=COLORS['text_secondary'], bg=COLORS['bg']).pack(side='left', padx=(0, 4))
        cat_var = tk.StringVar(value='Todas as categorias')
        combo_cat = ttk.Combobox(frame_filtros, textvariable=cat_var,
                                  values=cat_nomes, state='readonly', width=22,
                                  font=FONTS['small'])
        combo_cat.pack(side='left', padx=(0, 15))
        tk.Label(frame_filtros, text="🔍", font=FONTS['normal'],
                 bg=COLORS['bg']).pack(side='left', padx=(0, 4))
        entry_pq = ttk.Entry(frame_filtros, width=20, font=FONTS['normal'])
        entry_pq.pack(side='left')

        # Alerta stock baixo
        try:
            em_alerta = StockService(self.db).produtos_stock_baixo()
        except DatabaseError:
            em_alerta = []
        if em_alerta:
            fa = tk.Frame(parent, bg=COLORS['warning'], highlightthickness=1,
                          highlightbackground="#d97706")
            fa.pack(fill='x', padx=15, pady=(0, 4))
            tk.Label(fa, text=f"⚠️  {len(em_alerta)} produto(s) com stock baixo — "
                              + ", ".join(p.nome for p in em_alerta[:4]),
                     font=FONTS['small'], fg='white', bg=COLORS['warning']
                     ).pack(anchor='w', padx=10, pady=4)

        # ── Treeview ───────────────────────────────────────────────────
        container = tk.Frame(parent, bg=COLORS['bg_secondary'], relief='flat',
                             borderwidth=1, highlightthickness=1,
                             highlightbackground=COLORS['border_light'])
        container.pack(fill='both', expand=True, padx=15, pady=(0, 8))
        sb = ttk.Scrollbar(container)
        sb.pack(side='right', fill='y')

        colunas = ('id', 'categoria', 'nome', 'avaliacao', 'preco', 'stock', 'estado')
        tree = ttk.Treeview(container, columns=colunas, show='headings',
                            yscrollcommand=sb.set, selectmode='browse', height=15)
        tree.pack(side='left', fill='both', expand=True)
        sb.config(command=tree.yview)

        tree.heading('id',        text='ID',        anchor='center')
        tree.heading('categoria', text='Categoria', anchor='w')
        tree.heading('nome',      text='Nome',      anchor='w')
        tree.heading('avaliacao', text='Avaliação', anchor='center')
        tree.heading('preco',     text='Preço',     anchor='e')
        tree.heading('stock',     text='Stock',     anchor='center')
        tree.heading('estado',    text='Estado',    anchor='center')
        tree.column('id',        width=45,  anchor='center', stretch=False)
        tree.column('categoria', width=125, anchor='w',      stretch=False)
        tree.column('nome',      width=230, anchor='w',      stretch=True)
        tree.column('avaliacao', width=110, anchor='center', stretch=False)
        tree.column('preco',     width=90,  anchor='e',      stretch=False)
        tree.column('stock',     width=60,  anchor='center', stretch=False)
        tree.column('estado',    width=110, anchor='center', stretch=False)

        tree.tag_configure('odd',       background='#f8fafc')
        tree.tag_configure('even',      background='#ffffff')
        tree.tag_configure('hover',     background='#dbeafe', foreground=COLORS['primary'])
        tree.tag_configure('low_stock', background='#fff7ed', foreground=COLORS['warning'])

        produtos_visiveis: list[Produto] = []

        def _popular(filtro_nome='', filtro_cat='Todas as categorias'):
            nonlocal produtos_visiveis
            tree.delete(*tree.get_children())
            fl = filtro_nome.lower()
            produtos_visiveis = [
                p for p in todos_produtos
                if (fl in p.nome.lower() or fl == '')
                and (filtro_cat == 'Todas as categorias'
                     or (p.nome_categoria or '—') == filtro_cat)
            ]
            lbl_cont.config(text=f"{len(produtos_visiveis)} produto(s)")
            for i, p in enumerate(produtos_visiveis):
                tag = 'low_stock' if p.stock <= 3 else ('odd' if i % 2 == 0 else 'even')
                estado = "✅ OK" if p.stock > 3 else ("⚠️ Baixo" if p.stock > 0 else "❌ Esgotado")
                tree.insert('', 'end', iid=str(i),
                            values=(p.id_produto,
                                    p.nome_categoria or '—',
                                    f"  {p.nome}",
                                    _estrelas(p.id_produto),
                                    f"€ {p.preco:.2f}", p.stock, estado),
                            tags=(tag,))

        _popular()

        _hover: dict = {'iid': None, 'tags': ()}

        def _motion(e):
            iid = tree.identify_row(e.y)
            if iid == _hover['iid']:
                return
            if _hover['iid'] and tree.exists(_hover['iid']):
                tree.item(_hover['iid'], tags=_hover['tags'])
            if iid:
                _hover['iid'] = iid
                _hover['tags'] = tree.item(iid, 'tags')
                tree.item(iid, tags=('hover',))
            else:
                _hover['iid'] = None

        def _leave(e):
            if _hover['iid'] and tree.exists(_hover['iid']):
                tree.item(_hover['iid'], tags=_hover['tags'])
            _hover['iid'] = None

        tree.bind('<Motion>', _motion)
        tree.bind('<Leave>',  _leave)

        def _atualizar_filtros(*_):
            _leave(None)
            _popular(entry_pq.get().strip(), cat_var.get())

        entry_pq.bind('<KeyRelease>', _atualizar_filtros)
        combo_cat.bind('<<ComboboxSelected>>', _atualizar_filtros)

        def _produto_sel():
            sel = tree.selection()
            return produtos_visiveis[int(sel[0])] if sel else None

        # ── Diálogo partilhado (criar / editar) ────────────────────────
        def _abrir_dialogo_produto(produto_existente: Produto | None = None):
            eh_edicao = produto_existente is not None
            titulo_dlg = "✏️ Editar Produto" if eh_edicao else "➕ Novo Produto"

            janela = tk.Toplevel(self.master)
            janela.title(titulo_dlg)
            janela.geometry("560x560")
            janela.configure(bg=COLORS['bg'])
            janela.resizable(False, False)
            janela.transient(self.master)
            janela.grab_set()

            frame_main = tk.Frame(janela, bg=COLORS['bg'])
            frame_main.pack(fill='both', expand=True, padx=20, pady=20)

            tk.Label(frame_main, text=titulo_dlg,
                     font=FONTS['subtitle'], fg=COLORS['primary'],
                     bg=COLORS['bg']).pack(pady=(0, 16))

            # Categoria
            tk.Label(frame_main, text="🗂️  Categoria *",
                     font=FONTS['normal'], fg=COLORS['text_primary'],
                     bg=COLORS['bg']).pack(anchor='w')
            cat_sel_var = tk.StringVar()
            combo_cat_dlg = ttk.Combobox(frame_main, textvariable=cat_sel_var,
                                          values=[c.nome for c in cats],
                                          state='readonly', width=48,
                                          font=FONTS['normal'])
            combo_cat_dlg.pack(fill='x', pady=(4, 12))
            if eh_edicao and produto_existente.nome_categoria:
                cat_sel_var.set(produto_existente.nome_categoria)
            elif cats:
                cat_sel_var.set(cats[0].nome)

            # Nome
            tk.Label(frame_main, text="📝 Nome do Produto *",
                     font=FONTS['normal'], fg=COLORS['text_primary'],
                     bg=COLORS['bg']).pack(anchor='w')
            entry_nome = ttk.Entry(frame_main, width=50, font=FONTS['normal'])
            entry_nome.pack(fill='x', pady=(4, 12))
            if eh_edicao:
                entry_nome.insert(0, produto_existente.nome or '')
            entry_nome.focus()

            # Descrição
            tk.Label(frame_main, text="📄 Descrição",
                     font=FONTS['normal'], fg=COLORS['text_primary'],
                     bg=COLORS['bg']).pack(anchor='w')
            text_desc = tk.Text(frame_main, height=3, width=50, font=FONTS['small'],
                                bg=COLORS['bg_secondary'], fg=COLORS['text_primary'])
            text_desc.pack(fill='x', pady=(4, 12))
            if eh_edicao and produto_existente.descricao:
                text_desc.insert('1.0', produto_existente.descricao)

            # Preço + Stock
            frame_ps = tk.Frame(frame_main, bg=COLORS['bg'])
            frame_ps.pack(fill='x', pady=(0, 12))
            tk.Label(frame_ps, text="💵 Preço (€) *",
                     font=FONTS['normal'], fg=COLORS['text_primary'],
                     bg=COLORS['bg']).pack(side='left', padx=(0, 8))
            entry_preco = ttk.Entry(frame_ps, width=14, font=FONTS['normal'])
            entry_preco.pack(side='left')
            tk.Label(frame_ps, text="📦 Stock *",
                     font=FONTS['normal'], fg=COLORS['text_primary'],
                     bg=COLORS['bg']).pack(side='left', padx=(30, 8))
            entry_stock = ttk.Entry(frame_ps, width=14, font=FONTS['normal'])
            entry_stock.pack(side='left')
            if eh_edicao:
                entry_preco.insert(0, str(produto_existente.preco or ''))
                entry_stock.insert(0, str(produto_existente.stock or ''))

            lbl_status = tk.Label(frame_main, text="", font=FONTS['small'],
                                  bg=COLORS['bg'], fg=COLORS['danger'])
            lbl_status.pack(anchor='w', pady=(4, 8))

            def guardar():
                nome = entry_nome.get().strip()
                descricao = text_desc.get('1.0', 'end-1c').strip()
                preco_str = entry_preco.get().strip()
                stock_str = entry_stock.get().strip()
                cat_nome_sel = cat_sel_var.get()

                valido, msg = validar_nome_produto(nome)
                if not valido:
                    lbl_status.config(text=f"⚠️  {msg}"); return
                valido, preco, msg = validar_preco(preco_str)
                if not valido:
                    lbl_status.config(text=f"⚠️  {msg}"); return
                valido, stock, msg = validar_stock(stock_str)
                if not valido:
                    lbl_status.config(text=f"⚠️  {msg}"); return

                # Resolver id_categoria
                id_cat = next((c.id_categoria for c in cats if c.nome == cat_nome_sel), None)

                try:
                    if eh_edicao:
                        self.db.executar_update(
                            """UPDATE produtos
                               SET id_categoria=%s, nome=%s, descricao=%s,
                                   preco=%s, stock=%s
                             WHERE id_produto=%s""",
                            (id_cat, nome, descricao or None,
                             preco, stock, produto_existente.id_produto)
                        )
                        logger.info("Produto editado: id=%s '%s'",
                                    produto_existente.id_produto, nome)
                        lbl_status.config(
                            text=f"✅ Produto '{nome}' actualizado!",
                            fg=COLORS['success'])
                    else:
                        novo_id = self.db.executar_update(
                            """INSERT INTO produtos
                               (id_categoria, nome, descricao, preco, stock)
                               VALUES (%s, %s, %s, %s, %s)""",
                            (id_cat, nome, descricao or None, preco, stock)
                        )
                        logger.info("Produto criado: id=%s '%s'", novo_id, nome)
                        lbl_status.config(
                            text=f"✅ Produto '{nome}' adicionado! (ID: {novo_id})",
                            fg=COLORS['success'])
                    self.master.after(1200, lambda: janela.destroy())
                    self._criar_aba_gerir_produtos(parent)
                except DatabaseError as e:
                    logger.error("Erro BD ao guardar produto '%s': %s", nome, e)
                    lbl_status.config(text=f"❌ Erro: {e}", fg=COLORS['danger'])

            frame_btn = tk.Frame(frame_main, bg=COLORS['bg'])
            frame_btn.pack(fill='x')
            btn_g = tk.Button(frame_btn, text="✅ Guardar", command=guardar,
                              font=FONTS['normal'], bg=COLORS['success'], fg='white',
                              relief='flat', padx=30, pady=10, cursor='hand2')
            btn_g.pack(side='left', padx=5, fill='x', expand=True)
            tk.Button(frame_btn, text="❌ Cancelar", command=janela.destroy,
                      font=FONTS['normal'], bg=COLORS['danger'], fg='white',
                      relief='flat', padx=30, pady=10, cursor='hand2',
                      ).pack(side='left', padx=5, fill='x', expand=True)
            janela.bind('<Return>', lambda e: guardar())

        def editar_produto():
            p = _produto_sel()
            if not p:
                self.notify.warning("Selecione um produto para editar!")
                return
            _abrir_dialogo_produto(p)

        def eliminar_produto():
            p = _produto_sel()
            if not p:
                self.notify.warning("Selecione um produto para eliminar!")
                return
            def confirmar(resposta):
                if not resposta:
                    return
                try:
                    self.db.executar_update(
                        "DELETE FROM produtos WHERE id_produto = %s",
                        (p.id_produto,)
                    )
                    logger.info("Produto eliminado: id=%s '%s'", p.id_produto, p.nome)
                    self.notify.success(f"Produto '{p.nome}' eliminado.")
                    self._criar_aba_gerir_produtos(parent)
                except DatabaseError as e:
                    self.notify.error(f"Erro ao eliminar: {e}")
            self.notify.question(
                f"Eliminar o produto '{p.nome}'?\n(Esta acção é irreversível)",
                "Confirmar Eliminação", callback=confirmar)

        # ── Botões ──────────────────────────────────────────────────────
        frame_botoes = tk.Frame(parent, bg=COLORS['bg'])
        frame_botoes.pack(fill='x', padx=15, pady=(0, 12))

        btn_novo = tk.Button(frame_botoes, text="➕ Novo Produto",
                             command=lambda: _abrir_dialogo_produto(),
                             font=FONTS['normal'], bg=COLORS['success'], fg='white',
                             relief='flat', padx=20, pady=10, cursor='hand2',
                             activebackground='#059669')
        btn_novo.pack(side='left', padx=5)
        btn_novo.bind('<Enter>', lambda e: btn_novo.config(bg='#059669'))
        btn_novo.bind('<Leave>', lambda e: btn_novo.config(bg=COLORS['success']))

        btn_editar = tk.Button(frame_botoes, text="✏️ Editar",
                               command=editar_produto,
                               font=FONTS['normal'], bg=COLORS['primary'], fg='white',
                               relief='flat', padx=20, pady=10, cursor='hand2',
                               activebackground='#1d4ed8')
        btn_editar.pack(side='left', padx=5)
        btn_editar.bind('<Enter>', lambda e: btn_editar.config(bg='#1d4ed8'))
        btn_editar.bind('<Leave>', lambda e: btn_editar.config(bg=COLORS['primary']))

        btn_elim = tk.Button(frame_botoes, text="🗑️ Eliminar",
                             command=eliminar_produto,
                             font=FONTS['normal'], bg=COLORS['danger'], fg='white',
                             relief='flat', padx=20, pady=10, cursor='hand2',
                             activebackground='#dc2626')
        btn_elim.pack(side='left', padx=5)
        btn_elim.bind('<Enter>', lambda e: btn_elim.config(bg='#dc2626'))
        btn_elim.bind('<Leave>', lambda e: btn_elim.config(bg=COLORS['danger']))

        btn_reload = tk.Button(frame_botoes, text="🔄 Recarregar",
                               command=lambda: self._criar_aba_gerir_produtos(parent),
                               font=FONTS['normal'], bg=COLORS['info'], fg='white',
                               relief='flat', padx=20, pady=10, cursor='hand2',
                               activebackground='#0891b2')
        btn_reload.pack(side='left', padx=5)
        btn_reload.bind('<Enter>', lambda e: btn_reload.config(bg='#0891b2'))
        btn_reload.bind('<Leave>', lambda e: btn_reload.config(bg=COLORS['info']))

        btn_pdf = tk.Button(frame_botoes, text="📄 Exportar PDF",
                            command=lambda: self._exportar_pdf_stock(),
                            font=FONTS['normal'], bg=COLORS['success'], fg='white',
                            relief='flat', padx=20, pady=10, cursor='hand2',
                            activebackground='#059669')
        btn_pdf.pack(side='left', padx=5)
        btn_pdf.bind('<Enter>', lambda e: btn_pdf.config(bg='#059669'))
        btn_pdf.bind('<Leave>', lambda e: btn_pdf.config(bg=COLORS['success']))

        tree.bind('<Double-Button-1>', lambda e: editar_produto())

    # ──────────────────────────────────────────────────────────────────────────
    def _criar_aba_gerir_categorias(self, parent):
        """Cria aba para gerir categorias de produtos."""
        for widget in parent.winfo_children():
            widget.destroy()

        cat_repo = CategoriaRepository(self.db)

        def _carregar_cats():
            try:
                return cat_repo.listar_todos()
            except DatabaseError as e:
                logger.error("Erro ao carregar categorias: %s", e)
                self.notify.error(f"Erro ao carregar categorias: {e}")
                return []

        cats = _carregar_cats()

        # ── Cabeçalho ──────────────────────────────────────────────────
        frame_topo = tk.Frame(parent, bg=COLORS['bg'])
        frame_topo.pack(fill='x', padx=15, pady=(12, 6))
        tk.Label(frame_topo, text="Categorias de Produtos",
                 font=FONTS['subtitle'], fg=COLORS['primary'],
                 bg=COLORS['bg']).pack(side='left')
        lbl_cont = tk.Label(frame_topo, text=f"{len(cats)} categoria(s)",
                            font=FONTS['small'], fg=COLORS['text_secondary'],
                            bg=COLORS['bg'])
        lbl_cont.pack(side='right', padx=(0, 12))

        # ── Treeview ───────────────────────────────────────────────────
        container = tk.Frame(parent, bg=COLORS['bg_secondary'], relief='flat',
                             borderwidth=1, highlightthickness=1,
                             highlightbackground=COLORS['border_light'])
        container.pack(fill='both', expand=True, padx=15, pady=(0, 8))
        sb = ttk.Scrollbar(container)
        sb.pack(side='right', fill='y')

        colunas = ('id', 'nome', 'descricao', 'n_produtos')
        tree_c = ttk.Treeview(container, columns=colunas, show='headings',
                              yscrollcommand=sb.set, selectmode='browse', height=16)
        tree_c.pack(side='left', fill='both', expand=True)
        sb.config(command=tree_c.yview)

        tree_c.heading('id',         text='ID',        anchor='center')
        tree_c.heading('nome',       text='Nome',      anchor='w')
        tree_c.heading('descricao',  text='Descrição', anchor='w')
        tree_c.heading('n_produtos', text='Produtos',  anchor='center')
        tree_c.column('id',         width=45,  anchor='center', stretch=False)
        tree_c.column('nome',       width=160, anchor='w',      stretch=False)
        tree_c.column('descricao',  width=400, anchor='w',      stretch=True)
        tree_c.column('n_produtos', width=80,  anchor='center', stretch=False)

        tree_c.tag_configure('odd',  background='#f8fafc')
        tree_c.tag_configure('even', background='#ffffff')
        tree_c.tag_configure('hover', background='#dbeafe', foreground=COLORS['primary'])

        cats_lista: list = []

        def _popular():
            nonlocal cats_lista
            cats_lista = _carregar_cats()
            tree_c.delete(*tree_c.get_children())
            lbl_cont.config(text=f"{len(cats_lista)} categoria(s)")
            for i, c in enumerate(cats_lista):
                try:
                    n_p = cat_repo.contar_produtos(c.id_categoria)
                except DatabaseError:
                    n_p = '?'
                tag = 'odd' if i % 2 == 0 else 'even'
                tree_c.insert('', 'end', iid=str(i),
                              values=(c.id_categoria, c.nome,
                                      c.descricao or '—', n_p),
                              tags=(tag,))

        _popular()

        _hover_c: dict = {'iid': None, 'tags': ()}

        def _motion(e):
            iid = tree_c.identify_row(e.y)
            if iid == _hover_c['iid']: return
            if _hover_c['iid'] and tree_c.exists(_hover_c['iid']):
                tree_c.item(_hover_c['iid'], tags=_hover_c['tags'])
            if iid:
                _hover_c['iid'] = iid
                _hover_c['tags'] = tree_c.item(iid, 'tags')
                tree_c.item(iid, tags=('hover',))
            else:
                _hover_c['iid'] = None

        def _leave(e):
            if _hover_c['iid'] and tree_c.exists(_hover_c['iid']):
                tree_c.item(_hover_c['iid'], tags=_hover_c['tags'])
            _hover_c['iid'] = None

        tree_c.bind('<Motion>', _motion)
        tree_c.bind('<Leave>',  _leave)

        def _cat_sel():
            sel = tree_c.selection()
            return cats_lista[int(sel[0])] if sel else None

        # ── Diálogo partilhado (criar / editar) ────────────────────────
        def _abrir_dialogo_categoria(cat_existente=None):
            eh_edicao = cat_existente is not None
            titulo_dlg = "✏️ Editar Categoria" if eh_edicao else "➕ Nova Categoria"

            janela = tk.Toplevel(self.master)
            janela.title(titulo_dlg)
            janela.geometry("480x360")
            janela.configure(bg=COLORS['bg'])
            janela.resizable(False, False)
            janela.transient(self.master)
            janela.grab_set()

            frame_m = tk.Frame(janela, bg=COLORS['bg'])
            frame_m.pack(fill='both', expand=True, padx=20, pady=20)

            tk.Label(frame_m, text=titulo_dlg, font=FONTS['subtitle'],
                     fg=COLORS['primary'], bg=COLORS['bg']).pack(pady=(0, 16))

            tk.Label(frame_m, text="🏷️  Nome *", font=FONTS['normal'],
                     fg=COLORS['text_primary'], bg=COLORS['bg']).pack(anchor='w')
            entry_nome = ttk.Entry(frame_m, width=50, font=FONTS['normal'])
            entry_nome.pack(fill='x', pady=(4, 12))
            if eh_edicao:
                entry_nome.insert(0, cat_existente.nome or '')
            entry_nome.focus()

            tk.Label(frame_m, text="📄 Descrição", font=FONTS['normal'],
                     fg=COLORS['text_primary'], bg=COLORS['bg']).pack(anchor='w')
            text_desc = tk.Text(frame_m, height=4, width=50, font=FONTS['small'],
                                bg=COLORS['bg_secondary'], fg=COLORS['text_primary'])
            text_desc.pack(fill='x', pady=(4, 12))
            if eh_edicao and cat_existente.descricao:
                text_desc.insert('1.0', cat_existente.descricao)

            lbl_status = tk.Label(frame_m, text="", font=FONTS['small'],
                                  bg=COLORS['bg'], fg=COLORS['danger'])
            lbl_status.pack(anchor='w', pady=(4, 8))

            def guardar():
                from src.models.categoria import Categoria
                nome = entry_nome.get().strip()
                descricao = text_desc.get('1.0', 'end-1c').strip()
                if not nome:
                    lbl_status.config(text="⚠️  Nome obrigatório.")
                    return
                if len(nome) > 100:
                    lbl_status.config(text="⚠️  Nome demasiado longo (máx. 100).")
                    return
                try:
                    if eh_edicao:
                        cat_existente.nome = nome
                        cat_existente.descricao = descricao or None
                        cat_repo.atualizar(cat_existente)
                        lbl_status.config(text=f"✅ Categoria '{nome}' actualizada!",
                                          fg=COLORS['success'])
                    else:
                        nova = Categoria(nome=nome, descricao=descricao or None)
                        cat_repo.criar(nova)
                        lbl_status.config(text=f"✅ Categoria '{nome}' criada!",
                                          fg=COLORS['success'])
                    self.master.after(1200, lambda: janela.destroy())
                    _popular()
                except DatabaseError as e:
                    lbl_status.config(text=f"❌ Erro: {e}", fg=COLORS['danger'])

            frame_btn = tk.Frame(frame_m, bg=COLORS['bg'])
            frame_btn.pack(fill='x')
            tk.Button(frame_btn, text="✅ Guardar", command=guardar,
                      font=FONTS['normal'], bg=COLORS['success'], fg='white',
                      relief='flat', padx=30, pady=10, cursor='hand2',
                      ).pack(side='left', padx=5, fill='x', expand=True)
            tk.Button(frame_btn, text="❌ Cancelar", command=janela.destroy,
                      font=FONTS['normal'], bg=COLORS['danger'], fg='white',
                      relief='flat', padx=30, pady=10, cursor='hand2',
                      ).pack(side='left', padx=5, fill='x', expand=True)
            janela.bind('<Return>', lambda e: guardar())

        def editar_cat():
            c = _cat_sel()
            if not c:
                self.notify.warning("Selecione uma categoria para editar!")
                return
            _abrir_dialogo_categoria(c)

        def eliminar_cat():
            c = _cat_sel()
            if not c:
                self.notify.warning("Selecione uma categoria para eliminar!")
                return
            try:
                n_p = cat_repo.contar_produtos(c.id_categoria)
            except DatabaseError:
                n_p = 0
            aviso = ""
            if n_p:
                aviso = f"\n(⚠️  {n_p} produto(s) perderão a categoria)"
            def confirmar(resposta):
                if not resposta:
                    return
                try:
                    cat_repo.deletar(c.id_categoria)
                    self.notify.success(f"Categoria '{c.nome}' eliminada.")
                    _popular()
                except DatabaseError as e:
                    self.notify.error(f"Erro ao eliminar: {e}")
            self.notify.question(
                f"Eliminar a categoria '{c.nome}'?{aviso}",
                "Confirmar Eliminação", callback=confirmar)

        # ── Botões ──────────────────────────────────────────────────────
        frame_botoes = tk.Frame(parent, bg=COLORS['bg'])
        frame_botoes.pack(fill='x', padx=15, pady=(0, 12))

        for txt, cmd, cor in [
            ("➕ Nova Categoria",  lambda: _abrir_dialogo_categoria(), COLORS['success']),
            ("✏️ Editar",          editar_cat,                         COLORS['primary']),
            ("🗑️ Eliminar",        eliminar_cat,                       COLORS['danger']),
            ("🔄 Recarregar",      _popular,                            COLORS['info']),
        ]:
            b = tk.Button(frame_botoes, text=txt, command=cmd,
                          font=FONTS['normal'], bg=cor, fg='white',
                          relief='flat', padx=20, pady=10, cursor='hand2')
            b.pack(side='left', padx=5)
            dark = cor  # closure capture
            b.bind('<Enter>', lambda e, _b=b, _c=cor: _b.config(bg=_c))
            b.bind('<Leave>', lambda e, _b=b, _c=cor: _b.config(bg=_c))

        tree_c.bind('<Double-Button-1>', lambda e: editar_cat())

    # ──────────────────────────────────────────────────────────────────────────
    def _criar_aba_gerir_clientes(self, parent):
        """Cria aba para gerir clientes — tabela animada."""
        for widget in parent.winfo_children():
            widget.destroy()

        try:
            clientes_dados = self.db.executar_query(
                "SELECT id_cliente, nome, email, is_admin FROM clientes ORDER BY id_cliente"
            )
            clientes = [Cliente.from_dict(c) for c in clientes_dados] if clientes_dados else []
        except DatabaseError as e:
            logger.error("Erro ao carregar lista de clientes (admin): %s", e)
            self.notify.error(f"Erro ao carregar clientes: {e}")
            clientes = []

        frame_topo = tk.Frame(parent, bg=COLORS['bg'])
        frame_topo.pack(fill='x', padx=15, pady=(12, 6))
        tk.Label(frame_topo, text="Lista de Clientes",
                 font=FONTS['subtitle'], fg=COLORS['primary'],
                 bg=COLORS['bg']).pack(side='left')
        lbl_cont = tk.Label(frame_topo, text=f"{len(clientes)} cliente(s)",
                            font=FONTS['small'], fg=COLORS['text_secondary'],
                            bg=COLORS['bg'])
        lbl_cont.pack(side='right', padx=(0, 12))
        frame_pq = tk.Frame(frame_topo, bg=COLORS['bg'])
        frame_pq.pack(side='right')
        tk.Label(frame_pq, text="🔍", font=FONTS['normal'], bg=COLORS['bg']).pack(side='left', padx=(0, 4))
        entry_pq = ttk.Entry(frame_pq, width=20, font=FONTS['normal'])
        entry_pq.pack(side='left')

        container = tk.Frame(parent, bg=COLORS['bg_secondary'], relief='flat',
                             borderwidth=1, highlightthickness=1,
                             highlightbackground=COLORS['border_light'])
        container.pack(fill='both', expand=True, padx=15, pady=(0, 8))
        sb = ttk.Scrollbar(container)
        sb.pack(side='right', fill='y')

        colunas = ('id', 'nome', 'email', 'tipo')
        tree = ttk.Treeview(container, columns=colunas, show='headings',
                            yscrollcommand=sb.set, selectmode='browse', height=18)
        tree.pack(side='left', fill='both', expand=True)
        sb.config(command=tree.yview)

        tree.heading('id',    text='ID',     anchor='center')
        tree.heading('nome',  text='Nome',   anchor='w')
        tree.heading('email', text='Email',  anchor='w')
        tree.heading('tipo',  text='Perfil', anchor='center')
        tree.column('id',    width=55,  anchor='center', stretch=False)
        tree.column('nome',  width=240, anchor='w',      stretch=True)
        tree.column('email', width=320, anchor='w',      stretch=True)
        tree.column('tipo',  width=110, anchor='center', stretch=False)

        tree.tag_configure('odd',   background='#f8fafc')
        tree.tag_configure('even',  background='#ffffff')
        tree.tag_configure('hover', background='#dbeafe', foreground=COLORS['primary'])
        tree.tag_configure('admin', background='#eff6ff', foreground=COLORS['primary'])

        clientes_vis: list[Cliente] = []

        def _popular(filtro=''):
            nonlocal clientes_vis
            tree.delete(*tree.get_children())
            fl = filtro.lower()
            clientes_vis = [c for c in clientes
                            if fl in c.nome.lower() or fl in c.email.lower()] if filtro else list(clientes)
            lbl_cont.config(text=f"{len(clientes_vis)} cliente(s)")
            for i, c in enumerate(clientes_vis):
                tag = 'admin' if c.is_admin else ('odd' if i % 2 == 0 else 'even')
                perfil = "👨‍💼 Admin" if c.is_admin else "👤 Cliente"
                tree.insert('', 'end', iid=str(i),
                            values=(c.id_cliente, f"  {c.nome}", f"  {c.email}", perfil),
                            tags=(tag,))

        _popular()
        _hover: dict = {'iid': None, 'tags': ()}

        def _motion(e):
            iid = tree.identify_row(e.y)
            if iid == _hover['iid']:
                return
            if _hover['iid'] and tree.exists(_hover['iid']):
                tree.item(_hover['iid'], tags=_hover['tags'])
            if iid:
                _hover['iid'] = iid
                _hover['tags'] = tree.item(iid, 'tags')
                tree.item(iid, tags=('hover',))
            else:
                _hover['iid'] = None

        def _leave(e):
            if _hover['iid'] and tree.exists(_hover['iid']):
                tree.item(_hover['iid'], tags=_hover['tags'])
            _hover['iid'] = None

        tree.bind('<Motion>', _motion)
        tree.bind('<Leave>',  _leave)
        entry_pq.bind('<KeyRelease>', lambda e: (_leave(None), _popular(entry_pq.get().strip())))

        frame_botoes = tk.Frame(parent, bg=COLORS['bg'])
        frame_botoes.pack(fill='x', padx=15, pady=(0, 12))

        btn_recarregar = tk.Button(frame_botoes, text="🔄 Recarregar",
                                  command=lambda: self._criar_aba_gerir_clientes(parent),
                                  font=FONTS['normal'], bg=COLORS['info'], fg='white',
                                  relief='flat', padx=20, pady=10, cursor='hand2',
                                  activebackground='#0891b2')
        btn_recarregar.pack(side='left', padx=5)
        btn_recarregar.bind('<Enter>', lambda e: btn_recarregar.config(bg='#0891b2'))
        btn_recarregar.bind('<Leave>', lambda e: btn_recarregar.config(bg=COLORS['info']))
    
    def _criar_aba_vendas(self, parent):
        """Cria aba de vendas — tabela animada."""
        for widget in parent.winfo_children():
            widget.destroy()

        try:
            vendas = self.db.executar_query("""
                SELECT v.id_venda, c.nome, v.data, v.total
                FROM vendas v
                JOIN clientes c ON v.id_cliente = c.id_cliente
                ORDER BY v.data DESC, v.id_venda DESC
                LIMIT 200
            """)
        except DatabaseError as e:
            logger.error("Erro ao carregar histórico de vendas (admin): %s", e)
            self.notify.error(f"Erro ao carregar vendas: {e}")
            vendas = []
        vendas = vendas or []

        frame_topo = tk.Frame(parent, bg=COLORS['bg'])
        frame_topo.pack(fill='x', padx=15, pady=(12, 6))
        tk.Label(frame_topo, text="Histórico de Vendas",
                 font=FONTS['subtitle'], fg=COLORS['primary'],
                 bg=COLORS['bg']).pack(side='left')
        lbl_cont = tk.Label(frame_topo, text=f"{len(vendas)} venda(s)",
                            font=FONTS['small'], fg=COLORS['text_secondary'],
                            bg=COLORS['bg'])
        lbl_cont.pack(side='right', padx=(0, 12))
        frame_pq = tk.Frame(frame_topo, bg=COLORS['bg'])
        frame_pq.pack(side='right')
        tk.Label(frame_pq, text="🔍", font=FONTS['normal'], bg=COLORS['bg']).pack(side='left', padx=(0, 4))
        entry_pq = ttk.Entry(frame_pq, width=20, font=FONTS['normal'])
        entry_pq.pack(side='left')

        container = tk.Frame(parent, bg=COLORS['bg_secondary'], relief='flat',
                             borderwidth=1, highlightthickness=1,
                             highlightbackground=COLORS['border_light'])
        container.pack(fill='both', expand=True, padx=15, pady=(0, 8))
        sb = ttk.Scrollbar(container)
        sb.pack(side='right', fill='y')

        colunas = ('id', 'cliente', 'data', 'total')
        tree = ttk.Treeview(container, columns=colunas, show='headings',
                            yscrollcommand=sb.set, selectmode='browse', height=18)
        tree.pack(side='left', fill='both', expand=True)
        sb.config(command=tree.yview)

        tree.heading('id',      text='ID',      anchor='center')
        tree.heading('cliente', text='Cliente', anchor='w')
        tree.heading('data',    text='Data',    anchor='center')
        tree.heading('total',   text='Total',   anchor='e')
        tree.column('id',      width=60,  anchor='center', stretch=False)
        tree.column('cliente', width=320, anchor='w',      stretch=True)
        tree.column('data',    width=130, anchor='center', stretch=False)
        tree.column('total',   width=120, anchor='e',      stretch=False)

        tree.tag_configure('odd',   background='#f8fafc')
        tree.tag_configure('even',  background='#ffffff')
        tree.tag_configure('hover', background='#dbeafe', foreground=COLORS['primary'])

        vendas_vis: list[dict] = []

        def _popular(filtro=''):
            nonlocal vendas_vis
            tree.delete(*tree.get_children())
            fl = filtro.lower()
            vendas_vis = [v for v in vendas
                          if fl in v['nome'].lower() or fl in str(v['data'])] if filtro else list(vendas)
            lbl_cont.config(text=f"{len(vendas_vis)} venda(s)")
            for i, v in enumerate(vendas_vis):
                tag = 'odd' if i % 2 == 0 else 'even'
                tree.insert('', 'end', iid=str(i),
                            values=(v['id_venda'], f"  {v['nome']}",
                                    str(v['data']), f"€ {float(v['total']):.2f}"),
                            tags=(tag,))

        _popular()
        _hover: dict = {'iid': None, 'tags': ()}

        def _motion(e):
            iid = tree.identify_row(e.y)
            if iid == _hover['iid']:
                return
            if _hover['iid'] and tree.exists(_hover['iid']):
                tree.item(_hover['iid'], tags=_hover['tags'])
            if iid:
                _hover['iid'] = iid
                _hover['tags'] = tree.item(iid, 'tags')
                tree.item(iid, tags=('hover',))
            else:
                _hover['iid'] = None

        def _leave(e):
            if _hover['iid'] and tree.exists(_hover['iid']):
                tree.item(_hover['iid'], tags=_hover['tags'])
            _hover['iid'] = None

        tree.bind('<Motion>', _motion)
        tree.bind('<Leave>',  _leave)
        entry_pq.bind('<KeyRelease>', lambda e: (_leave(None), _popular(entry_pq.get().strip())))

        frame_botoes = tk.Frame(parent, bg=COLORS['bg'])
        frame_botoes.pack(fill='x', padx=15, pady=(0, 12))

        btn_recarregar = tk.Button(frame_botoes, text="🔄 Recarregar",
                                  command=lambda: self._criar_aba_vendas(parent),
                                  font=FONTS['normal'], bg=COLORS['info'], fg='white',
                                  relief='flat', padx=20, pady=10, cursor='hand2',
                                  activebackground='#0891b2')
        btn_recarregar.pack(side='left', padx=5)
        btn_recarregar.bind('<Enter>', lambda e: btn_recarregar.config(bg='#0891b2'))
        btn_recarregar.bind('<Leave>', lambda e: btn_recarregar.config(bg=COLORS['info']))

        btn_pdf = tk.Button(frame_botoes, text="📄 Exportar PDF",
                            command=lambda: self._exportar_pdf_vendas(),
                            font=FONTS['normal'], bg=COLORS['success'], fg='white',
                            relief='flat', padx=20, pady=10, cursor='hand2',
                            activebackground='#059669')
        btn_pdf.pack(side='left', padx=5)
        btn_pdf.bind('<Enter>', lambda e: btn_pdf.config(bg='#059669'))
        btn_pdf.bind('<Leave>', lambda e: btn_pdf.config(bg=COLORS['success']))

    # ------------------------------------------------------------------
    # Exportação PDF
    # ------------------------------------------------------------------

    def _exportar_pdf_vendas(self) -> None:
        """Gera e guarda em disco o relatório PDF do histórico de vendas."""
        caminho = filedialog.asksaveasfilename(
            title="Guardar Relatório de Vendas",
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            initialfile=f"vendas_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        )
        if not caminho:
            return

        try:
            vendas = self.db.executar_query("""
                SELECT v.id_venda, c.nome, v.data, v.total
                FROM vendas v
                JOIN clientes c ON v.id_cliente = c.id_cliente
                ORDER BY v.data DESC, v.id_venda DESC
                LIMIT 500
            """)
            svc = RelatorioService()
            conteudo = svc.relatorio_vendas(vendas)
            svc.guardar(conteudo, caminho)
            self.notify.success(f"PDF guardado em:\n{caminho}")
            logger.info("Relatório de vendas exportado: %s", caminho)
        except DatabaseError as e:
            logger.error("Erro ao exportar PDF de vendas: %s", e)
            self.notify.error(f"Erro ao exportar: {e}")
        except OSError as e:
            logger.error("Erro ao guardar PDF de vendas: %s", e)
            self.notify.error(f"Erro ao guardar ficheiro: {e}")

    def _exportar_pdf_stock(self) -> None:
        """Gera e guarda em disco o relatório PDF do inventário de stock."""
        caminho = filedialog.asksaveasfilename(
            title="Guardar Relatório de Stock",
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            initialfile=f"stock_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        )
        if not caminho:
            return

        try:
            from src.repositories.produto_repository import ProdutoRepository
            produtos = ProdutoRepository(self.db).listar_todos()
            svc = RelatorioService()
            conteudo = svc.relatorio_stock(produtos)
            svc.guardar(conteudo, caminho)
            self.notify.success(f"PDF guardado em:\n{caminho}")
            logger.info("Relatório de stock exportado: %s", caminho)
        except DatabaseError as e:
            logger.error("Erro ao exportar PDF de stock: %s", e)
            self.notify.error(f"Erro ao exportar: {e}")
        except OSError as e:
            logger.error("Erro ao guardar PDF de stock: %s", e)
            self.notify.error(f"Erro ao guardar ficheiro: {e}")

    def _criar_aba_gerir_cupoes(self, parent):
        """Cria aba de gestão de cupões — tabela animada."""
        for widget in parent.winfo_children():
            widget.destroy()

        repo = CupaoRepository(self.db)
        try:
            cupoes = repo.listar_todos()
        except DatabaseError as e:
            logger.error("Erro ao carregar cupões: %s", e)
            self.notify.error(f"Erro ao carregar cupões: {e}")
            cupoes = []

        frame_topo = tk.Frame(parent, bg=COLORS['bg'])
        frame_topo.pack(fill='x', padx=15, pady=(12, 6))
        tk.Label(frame_topo, text="Cupões de Desconto",
                 font=FONTS['subtitle'], fg=COLORS['primary'],
                 bg=COLORS['bg']).pack(side='left')
        lbl_cont = tk.Label(frame_topo, text=f"{len(cupoes)} cupão(s)",
                            font=FONTS['small'], fg=COLORS['text_secondary'],
                            bg=COLORS['bg'])
        lbl_cont.pack(side='right', padx=(0, 12))
        frame_pq = tk.Frame(frame_topo, bg=COLORS['bg'])
        frame_pq.pack(side='right')
        tk.Label(frame_pq, text="🔍", font=FONTS['normal'], bg=COLORS['bg']).pack(side='left', padx=(0, 4))
        entry_pq = ttk.Entry(frame_pq, width=18, font=FONTS['normal'])
        entry_pq.pack(side='left')

        container = tk.Frame(parent, bg=COLORS['bg_secondary'], relief='flat',
                             borderwidth=1, highlightthickness=1,
                             highlightbackground=COLORS['border_light'])
        container.pack(fill='both', expand=True, padx=15, pady=(0, 8))
        sb = ttk.Scrollbar(container)
        sb.pack(side='right', fill='y')

        colunas = ('id', 'codigo', 'desconto', 'tipo', 'validade', 'estado')
        tree = ttk.Treeview(container, columns=colunas, show='headings',
                            yscrollcommand=sb.set, selectmode='browse', height=16)
        tree.pack(side='left', fill='both', expand=True)
        sb.config(command=tree.yview)

        tree.heading('id',       text='ID',       anchor='center')
        tree.heading('codigo',   text='Código',   anchor='w')
        tree.heading('desconto', text='Desconto', anchor='center')
        tree.heading('tipo',     text='Tipo',     anchor='center')
        tree.heading('validade', text='Validade', anchor='center')
        tree.heading('estado',   text='Estado',   anchor='center')
        tree.column('id',       width=55,  anchor='center', stretch=False)
        tree.column('codigo',   width=180, anchor='w',      stretch=True)
        tree.column('desconto', width=100, anchor='center', stretch=False)
        tree.column('tipo',     width=120, anchor='center', stretch=False)
        tree.column('validade', width=130, anchor='center', stretch=False)
        tree.column('estado',   width=100, anchor='center', stretch=False)

        tree.tag_configure('odd',      background='#f8fafc')
        tree.tag_configure('even',     background='#ffffff')
        tree.tag_configure('hover',    background='#dbeafe', foreground=COLORS['primary'])
        tree.tag_configure('inativo',  background='#fef2f2', foreground=COLORS['danger'])

        cupoes_vis: list = []

        def _popular(filtro=''):
            nonlocal cupoes_vis
            tree.delete(*tree.get_children())
            fl = filtro.lower()
            cupoes_vis = [c for c in cupoes if fl in c.codigo.lower()] if filtro else list(cupoes)
            lbl_cont.config(text=f"{len(cupoes_vis)} cupão(s)")
            for i, c in enumerate(cupoes_vis):
                desconto_fmt = f"{c.desconto:.0f}%" if c.tipo == "percentagem" else f"€{c.desconto:.2f}"
                validade = str(c.data_validade) if c.data_validade else "Sem limite"
                estado = "✅ Activo" if c.ativo else "❌ Inactivo"
                tag = ('inativo',) if not c.ativo else ('odd' if i % 2 == 0 else 'even',)
                tree.insert('', 'end', iid=str(i),
                            values=(c.id_cupao, f"  {c.codigo}", desconto_fmt,
                                    c.tipo, validade, estado),
                            tags=tag)

        _popular()
        _hover: dict = {'iid': None, 'tags': ()}

        def _motion(e):
            iid = tree.identify_row(e.y)
            if iid == _hover['iid']:
                return
            if _hover['iid'] and tree.exists(_hover['iid']):
                tree.item(_hover['iid'], tags=_hover['tags'])
            if iid:
                _hover['iid'] = iid
                _hover['tags'] = tree.item(iid, 'tags')
                tree.item(iid, tags=('hover',))
            else:
                _hover['iid'] = None

        def _leave(e):
            if _hover['iid'] and tree.exists(_hover['iid']):
                tree.item(_hover['iid'], tags=_hover['tags'])
            _hover['iid'] = None

        tree.bind('<Motion>', _motion)
        tree.bind('<Leave>',  _leave)
        entry_pq.bind('<KeyRelease>', lambda e: (_leave(None), _popular(entry_pq.get().strip())))

        frame_botoes = tk.Frame(parent, bg=COLORS['bg'])
        frame_botoes.pack(fill='x', padx=15, pady=(0, 12))

        def novo_cupao():
            janela = tk.Toplevel(self.master)
            janela.title("🎟️ Novo Cupão")
            janela.geometry("480x400")
            janela.configure(bg=COLORS['bg'])

            frame = tk.Frame(janela, bg=COLORS['bg'])
            frame.pack(fill='both', expand=True, padx=20, pady=20)

            tk.Label(frame, text="🎟️ Novo Cupão de Desconto",
                     font=FONTS['subtitle'], fg=COLORS['primary'],
                     bg=COLORS['bg']).pack(pady=(0, 15))

            # Código
            tk.Label(frame, text="Código *", font=FONTS['normal'],
                     fg=COLORS['text_primary'], bg=COLORS['bg']).pack(anchor='w')
            entry_codigo = ttk.Entry(frame, width=25, font=FONTS['normal'])
            entry_codigo.pack(fill='x', pady=(2, 10))
            entry_codigo.focus()

            # Desconto + Tipo
            frame_desc = tk.Frame(frame, bg=COLORS['bg'])
            frame_desc.pack(fill='x', pady=(0, 10))

            tk.Label(frame_desc, text="Desconto *", font=FONTS['normal'],
                     fg=COLORS['text_primary'], bg=COLORS['bg']).pack(side='left')
            entry_desconto = ttk.Entry(frame_desc, width=10, font=FONTS['normal'])
            entry_desconto.pack(side='left', padx=(5, 20))

            tk.Label(frame_desc, text="Tipo", font=FONTS['normal'],
                     fg=COLORS['text_primary'], bg=COLORS['bg']).pack(side='left')
            tipo_var = tk.StringVar(value="percentagem")
            combo_tipo = ttk.Combobox(frame_desc, textvariable=tipo_var,
                                       values=["percentagem", "fixo"], width=14,
                                       state='readonly')
            combo_tipo.pack(side='left', padx=5)

            # Validade
            tk.Label(frame, text="Validade (AAAA-MM-DD, opcional)",
                     font=FONTS['normal'], fg=COLORS['text_primary'],
                     bg=COLORS['bg']).pack(anchor='w')
            entry_validade = ttk.Entry(frame, width=20, font=FONTS['normal'])
            entry_validade.pack(fill='x', pady=(2, 10))

            label_status = tk.Label(frame, text="", bg=COLORS['bg'],
                                    font=FONTS['normal'])
            label_status.pack(anchor='w', pady=5)

            def guardar():
                from datetime import date as _date
                codigo = entry_codigo.get().strip().upper()
                if not codigo:
                    label_status.config(text="⚠️  Código obrigatório.",
                                        fg=COLORS['danger'])
                    return
                try:
                    desconto = float(entry_desconto.get().replace(',', '.'))
                    if desconto <= 0:
                        raise ValueError
                except ValueError:
                    label_status.config(text="⚠️  Desconto inválido (ex: 10).",
                                        fg=COLORS['danger'])
                    return

                validade_str = entry_validade.get().strip() or None
                validade_dt = None
                if validade_str:
                    try:
                        validade_dt = _date.fromisoformat(validade_str)
                    except ValueError:
                        label_status.config(text="⚠️  Data inválida (use AAAA-MM-DD).",
                                            fg=COLORS['danger'])
                        return

                novo = Cupao(codigo=codigo, desconto=desconto,
                             tipo=tipo_var.get(), ativo=True,
                             data_validade=validade_dt)
                try:
                    repo.criar(novo)
                    label_status.config(
                        text=f"✅ Cupão '{codigo}' criado!",
                        fg=COLORS['success'])
                    janela.after(1200, janela.destroy)
                    self._criar_aba_gerir_cupoes(parent)
                except DatabaseError as e:
                    logger.error("Erro ao criar cupão '%s': %s", codigo, e)
                    label_status.config(text=f"❌ Erro: {e}", fg=COLORS['danger'])

            frame_btn = tk.Frame(frame, bg=COLORS['bg'])
            frame_btn.pack(fill='x', pady=10)
            tk.Button(frame_btn, text="✅ Guardar", command=guardar,
                      font=FONTS['normal'], bg=COLORS['success'], fg='white',
                      relief='flat', padx=20, pady=8, cursor='hand2').pack(side='left', padx=5)
            tk.Button(frame_btn, text="❌ Cancelar", command=janela.destroy,
                      font=FONTS['normal'], bg=COLORS['danger'], fg='white',
                      relief='flat', padx=20, pady=8, cursor='hand2').pack(side='left', padx=5)
            janela.bind('<Return>', lambda _: guardar())

        def desativar_cupao():
            codigo = tk.simpledialog.askstring(
                "Desactivar Cupão", "Código do cupão a desactivar:",
                parent=self.master)
            if not codigo:
                return
            c = repo.buscar_por_codigo(codigo)
            if c is None:
                self.notify.error(f"Cupão '{codigo.upper()}' não encontrado.")
                return
            repo.desativar(c.id_cupao)
            self.notify.success(f"Cupão '{c.codigo}' desactivado.")
            self._criar_aba_gerir_cupoes(parent)

        tk.Button(frame_botoes, text="➕ Novo Cupão",
                  command=novo_cupao,
                  font=FONTS['normal'], bg=COLORS['success'], fg='white',
                  relief='flat', padx=20, pady=10, cursor='hand2').pack(side='left', padx=5)

        tk.Button(frame_botoes, text="⛔ Desactivar",
                  command=desativar_cupao,
                  font=FONTS['normal'], bg=COLORS['danger'], fg='white',
                  relief='flat', padx=20, pady=10, cursor='hand2').pack(side='left', padx=5)

        tk.Button(frame_botoes, text="🔄 Recarregar",
                  command=lambda: self._criar_aba_gerir_cupoes(parent),
                  font=FONTS['normal'], bg=COLORS['info'], fg='white',
                  relief='flat', padx=20, pady=10, cursor='hand2').pack(side='left', padx=5)

    # ------------------------------------------------------------------
    # Wishlist
    # ------------------------------------------------------------------

    def _criar_aba_wishlist(self, parent):
        """Cria aba da wishlist (lista de desejos) do cliente."""
        for widget in parent.winfo_children():
            widget.destroy()

        tk.Label(parent, text="❤️  A Minha Wishlist",
                 font=FONTS['subtitle'], fg=COLORS['primary'],
                 bg=COLORS['bg']).pack(anchor='w', padx=15, pady=(15, 3))
        tk.Label(parent, text="Produtos que guardou para comprar mais tarde",
                 font=FONTS['small'], fg=COLORS['text_secondary'],
                 bg=COLORS['bg']).pack(anchor='w', padx=15, pady=(0, 10))

        container = tk.Frame(parent, bg=COLORS['bg_secondary'],
                            relief='flat', borderwidth=1,
                            highlightthickness=1,
                            highlightbackground=COLORS['border_light'])
        container.pack(fill='both', expand=True, padx=15, pady=(0, 15))

        scrollbar = ttk.Scrollbar(container)
        scrollbar.pack(side='right', fill='y')
        listbox = tk.Listbox(container, yscrollcommand=scrollbar.set,
                             height=18, font=FONTS['small'],
                             bg=COLORS['bg_secondary'],
                             fg=COLORS['text_primary'],
                             selectbackground='#e11d48',
                             selectforeground='white',
                             borderwidth=0)
        listbox.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.config(command=listbox.yview)

        try:
            linhas = self.db.executar_query("""
                SELECT w.id_wishlist, p.id_produto, p.nome, p.preco, p.stock
                FROM wishlist w
                JOIN produtos p ON p.id_produto = w.id_produto
                WHERE w.id_cliente = %s
                ORDER BY p.nome
            """, (self.usuario_atual.id_cliente,))
            itens_wishlist = linhas or []
        except DatabaseError as e:
            logger.error("Erro ao carregar wishlist: %s", e)
            self.notify.error(f"Erro ao carregar wishlist: {e}")
            itens_wishlist = []

        if not itens_wishlist:
            listbox.insert('end', "   A sua wishlist está vazia.")
            listbox.insert('end', "   Explore produtos e clique em '❤️ Wishlist'.")
        else:
            for item in itens_wishlist:
                stock_txt = f"Stock: {item['stock']}" if item['stock'] > 0 else "⚠️ Esgotado"
                listbox.insert('end',
                    f"  {item['nome']:<35} €{float(item['preco']):>8.2f}  │  {stock_txt}")

        frame_botoes = tk.Frame(parent, bg=COLORS['bg'])
        frame_botoes.pack(fill='x', padx=15, pady=(0, 15))

        def mover_para_carrinho():
            sel = listbox.curselection()
            if not sel:
                self.notify.warning("Selecione um produto!")
                return
            if not itens_wishlist:
                return
            item = itens_wishlist[sel[0]]
            if item['stock'] <= 0:
                self.notify.warning(f"'{item['nome']}' está esgotado!")
                return
            self.carrinho.append(Produto.from_dict(item))
            self._atualizar_aba_carrinho()
            self.notify.success(f"'{item['nome']}' adicionado ao carrinho!")

        def remover_da_wishlist():
            sel = listbox.curselection()
            if not sel:
                self.notify.warning("Selecione um produto!")
                return
            if not itens_wishlist:
                return
            item = itens_wishlist[sel[0]]
            def confirmar(resp):
                if resp:
                    try:
                        self.db.executar_update(
                            "DELETE FROM wishlist WHERE id_wishlist = %s",
                            (item['id_wishlist'],)
                        )
                        self.notify.success(f"'{item['nome']}' removido da wishlist!")
                        self._criar_aba_wishlist(parent)
                    except DatabaseError as e:
                        logger.error("Erro ao remover da wishlist: %s", e)
                        self.notify.error(f"Erro: {e}")
            self.notify.question(f"Remover '{item['nome']}' da wishlist?",
                                "Remover da Wishlist", callback=confirmar)

        btn_carrinho = tk.Button(frame_botoes, text="🛒 Mover para Carrinho",
                                command=mover_para_carrinho,
                                font=FONTS['normal'], bg=COLORS['success'], fg='white',
                                relief='flat', padx=20, pady=10, cursor='hand2',
                                activebackground='#059669')
        btn_carrinho.pack(side='left', padx=5)
        btn_carrinho.bind('<Enter>', lambda e: btn_carrinho.config(bg='#059669'))
        btn_carrinho.bind('<Leave>', lambda e: btn_carrinho.config(bg=COLORS['success']))

        btn_remover = tk.Button(frame_botoes, text="🗑️  Remover",
                               command=remover_da_wishlist,
                               font=FONTS['normal'], bg=COLORS['danger'], fg='white',
                               relief='flat', padx=20, pady=10, cursor='hand2',
                               activebackground='#dc2626')
        btn_remover.pack(side='left', padx=5)
        btn_remover.bind('<Enter>', lambda e: btn_remover.config(bg='#dc2626'))
        btn_remover.bind('<Leave>', lambda e: btn_remover.config(bg=COLORS['danger']))

        btn_recarregar = tk.Button(frame_botoes, text="🔄 Recarregar",
                                  command=lambda: self._criar_aba_wishlist(parent),
                                  font=FONTS['normal'], bg=COLORS['info'], fg='white',
                                  relief='flat', padx=20, pady=10, cursor='hand2',
                                  activebackground='#0891b2')
        btn_recarregar.pack(side='left', padx=5)
        btn_recarregar.bind('<Enter>', lambda e: btn_recarregar.config(bg='#0891b2'))
        btn_recarregar.bind('<Leave>', lambda e: btn_recarregar.config(bg=COLORS['info']))

    # ------------------------------------------------------------------
    # Avaliações
    # ------------------------------------------------------------------

    def _criar_aba_avaliacoes(self, parent):
        """Cria aba de avaliações públicas — todos os clientes vêem, só compradores avaliam."""
        for widget in parent.winfo_children():
            widget.destroy()

        tk.Label(parent, text="⭐ Avaliações de Produtos",
                 font=FONTS['subtitle'], fg=COLORS['primary'],
                 bg=COLORS['bg']).pack(anchor='w', padx=15, pady=(15, 3))
        tk.Label(parent,
                 text="Avaliações dos produtos que comprou — só pode avaliar produtos que comprou",
                 font=FONTS['small'], fg=COLORS['text_secondary'],
                 bg=COLORS['bg']).pack(anchor='w', padx=15, pady=(0, 8))

        ESTRELAS = {1: '★', 2: '★★', 3: '★★★', 4: '★★★★', 5: '★★★★★'}

        # ── Treeview de produtos com médias ──────────────────────────
        frame_top = tk.Frame(parent, bg=COLORS['bg'])
        frame_top.pack(fill='x', padx=15)

        tk.Label(frame_top, text="Produtos",
                 font=FONTS['small'], fg=COLORS['text_secondary'],
                 bg=COLORS['bg']).pack(anchor='w')

        frame_tree_prods = tk.Frame(frame_top, bg=COLORS['bg'])
        frame_tree_prods.pack(fill='x')

        cols_prods = ('nome', 'media', 'total', 'minha_nota')
        tree_prods = ttk.Treeview(frame_tree_prods, columns=cols_prods,
                                   show='headings', height=7, selectmode='browse')
        tree_prods.heading('nome',       text='Produto',       anchor='w')
        tree_prods.heading('media',      text='Média ⭐',      anchor='center')
        tree_prods.heading('total',      text='Nº Aval.',      anchor='center')
        tree_prods.heading('minha_nota', text='A Minha Nota',  anchor='center')
        tree_prods.column('nome',       width=260, stretch=True,  anchor='w')
        tree_prods.column('media',      width=130, stretch=False, anchor='center')
        tree_prods.column('total',      width=80,  stretch=False, anchor='center')
        tree_prods.column('minha_nota', width=130, stretch=False, anchor='center')

        sb_prods = ttk.Scrollbar(frame_tree_prods, orient='vertical',
                                  command=tree_prods.yview)
        tree_prods.configure(yscrollcommand=sb_prods.set)
        tree_prods.pack(side='left', fill='x', expand=True)
        sb_prods.pack(side='left', fill='y')

        # ── Treeview de reviews do produto selecionado ───────────────
        frame_bot = tk.Frame(parent, bg=COLORS['bg'])
        frame_bot.pack(fill='both', expand=True, padx=15, pady=(8, 0))

        lbl_sel = tk.Label(frame_bot,
                           text="↑ Selecione um produto para ver as avaliações",
                           font=FONTS['small'], fg=COLORS['text_secondary'],
                           bg=COLORS['bg'])
        lbl_sel.pack(anchor='w')

        frame_tree_rev = tk.Frame(frame_bot, bg=COLORS['bg_secondary'],
                                   relief='flat', borderwidth=1,
                                   highlightthickness=1,
                                   highlightbackground=COLORS['border_light'])
        frame_tree_rev.pack(fill='both', expand=True)

        cols_rev = ('cliente', 'nota', 'comentario', 'data')
        tree_rev = ttk.Treeview(frame_tree_rev, columns=cols_rev,
                                  show='headings', height=6, selectmode='none')
        tree_rev.heading('cliente',    text='Cliente',    anchor='w')
        tree_rev.heading('nota',       text='Nota',       anchor='center')
        tree_rev.heading('comentario', text='Comentário', anchor='w')
        tree_rev.heading('data',       text='Data',       anchor='center')
        tree_rev.column('cliente',    width=140, stretch=False, anchor='w')
        tree_rev.column('nota',       width=110, stretch=False, anchor='center')
        tree_rev.column('comentario', width=300, stretch=True,  anchor='w')
        tree_rev.column('data',       width=100, stretch=False, anchor='center')

        sb_rev = ttk.Scrollbar(frame_tree_rev, orient='vertical',
                                command=tree_rev.yview)
        tree_rev.configure(yscrollcommand=sb_rev.set)
        tree_rev.pack(side='left', fill='both', expand=True)
        sb_rev.pack(side='left', fill='y')

        # ── Botões ───────────────────────────────────────────────────
        frame_botoes = tk.Frame(parent, bg=COLORS['bg'])
        frame_botoes.pack(fill='x', padx=15, pady=(6, 15))

        # Estado da seleção atual
        estado = {'id_produto': None, 'nome': None,
                  'comprou': False, 'minha_nota': None, 'meu_comentario': None}

        def avaliar():
            if not estado['id_produto'] or not estado['comprou']:
                return
            self._dialog_avaliar_produto(
                id_produto=estado['id_produto'],
                nome_produto=estado['nome'],
                nota_atual=estado['minha_nota'],
                comentario_atual=estado['meu_comentario'],
                callback=lambda: self._criar_aba_avaliacoes(parent)
            )

        btn_avaliar = tk.Button(frame_botoes, text="⭐ Avaliar / Editar",
                                command=avaliar, state='disabled',
                                font=FONTS['normal'],
                                bg=COLORS['disabled'], fg='white',
                                relief='flat', padx=20, pady=10, cursor='hand2',
                                activebackground='#d97706',
                                disabledforeground='white')
        btn_avaliar.pack(side='left', padx=5)

        btn_reload = tk.Button(frame_botoes, text="🔄 Recarregar",
                               command=lambda: self._criar_aba_avaliacoes(parent),
                               font=FONTS['normal'], bg=COLORS['info'], fg='white',
                               relief='flat', padx=20, pady=10, cursor='hand2',
                               activebackground='#0891b2')
        btn_reload.pack(side='left', padx=5)
        btn_reload.bind('<Enter>', lambda e: btn_reload.config(bg='#0891b2'))
        btn_reload.bind('<Leave>', lambda e: btn_reload.config(bg=COLORS['info']))

        tk.Label(frame_botoes,
                 text="ℹ️  Só pode avaliar produtos que comprou",
                 font=FONTS['small'], fg=COLORS['text_secondary'],
                 bg=COLORS['bg']).pack(side='left', padx=10)

        # ── Carregar apenas produtos comprados pelo cliente, com média e a nota dele ─
        try:
            produtos_data = self.db.executar_query("""
                SELECT p.id_produto, p.nome,
                       ROUND(AVG(a.nota), 1)         AS media,
                       COUNT(a.id_avaliacao)          AS total_avaliacoes,
                       MAX(CASE WHEN a.id_cliente = %s THEN a.nota       END) AS minha_nota,
                       MAX(CASE WHEN a.id_cliente = %s THEN a.comentario END) AS meu_comentario
                FROM produtos p
                INNER JOIN (
                    SELECT DISTINCT vp.id_produto
                    FROM venda_produto vp
                    JOIN vendas v ON v.id_venda = vp.id_venda
                    WHERE v.id_cliente = %s
                ) AS comprados ON comprados.id_produto = p.id_produto
                LEFT JOIN avaliacoes a ON a.id_produto = p.id_produto
                GROUP BY p.id_produto, p.nome
                ORDER BY p.nome
            """, (self.usuario_atual.id_cliente, self.usuario_atual.id_cliente,
                  self.usuario_atual.id_cliente))
        except DatabaseError as e:
            logger.error("Erro ao carregar produtos para avaliações: %s", e)
            self.notify.error(f"Erro ao carregar avaliações: {e}")
            produtos_data = []

        for p in produtos_data:
            if p['media']:
                estrelas_med = ESTRELAS.get(round(float(p['media'])), '')
                media_txt = f"{estrelas_med}  {p['media']}/5"
            else:
                media_txt = "Sem avaliações"
            minha_txt = (f"{ESTRELAS.get(p['minha_nota'], '')}  {p['minha_nota']}/5"
                         if p['minha_nota'] else '—')
            tree_prods.insert('', 'end', iid=str(p['id_produto']),
                              values=(p['nome'], media_txt,
                                      p['total_avaliacoes'] or 0, minha_txt))

        def _carregar_reviews(id_prod):
            for row in tree_rev.get_children():
                tree_rev.delete(row)
            try:
                reviews = self.db.executar_query("""
                    SELECT c.nome AS cliente_nome, a.nota, a.comentario,
                           DATE_FORMAT(a.data_criacao, '%%d/%%m/%%Y') AS data_fmt
                    FROM avaliacoes a
                    JOIN clientes c ON c.id_cliente = a.id_cliente
                    WHERE a.id_produto = %s
                    ORDER BY a.data_criacao DESC
                """, (id_prod,))
            except DatabaseError as e:
                logger.error("Erro ao carregar reviews do produto: %s", e)
                reviews = []
            if reviews:
                for r in reviews:
                    nota_txt = f"{ESTRELAS.get(r['nota'], '?')}  ({r['nota']}/5)"
                    tree_rev.insert('', 'end',
                                    values=(r['cliente_nome'], nota_txt,
                                            r['comentario'] or '—', r['data_fmt']))
            else:
                tree_rev.insert('', 'end', values=('—', 'Sem avaliações', '—', '—'))

        def on_select_produto(event):
            sel = tree_prods.selection()
            if not sel:
                return
            id_prod = int(sel[0])
            pd = next((p for p in produtos_data if p['id_produto'] == id_prod), None)
            if not pd:
                return
            estado['id_produto'] = id_prod
            estado['nome'] = pd['nome']
            estado['minha_nota'] = pd['minha_nota']
            estado['meu_comentario'] = pd['meu_comentario']
            lbl_sel.config(text=f"Avaliações de: {pd['nome']}",
                           fg=COLORS['primary'], font=FONTS['normal'])
            # Verificar se o cliente comprou este produto
            try:
                res = self.db.executar_query("""
                    SELECT COUNT(*) AS total
                    FROM venda_produto vp
                    JOIN vendas v ON v.id_venda = vp.id_venda
                    WHERE v.id_cliente = %s AND vp.id_produto = %s
                """, (self.usuario_atual.id_cliente, id_prod))
                comprou = bool(res and res[0]['total'] > 0)
            except DatabaseError:
                comprou = False
            estado['comprou'] = comprou
            if comprou:
                btn_avaliar.config(state='normal', bg=COLORS['warning'])
                btn_avaliar.bind('<Enter>', lambda e: btn_avaliar.config(bg='#d97706'))
                btn_avaliar.bind('<Leave>', lambda e: btn_avaliar.config(bg=COLORS['warning']))
            else:
                btn_avaliar.config(state='disabled', bg=COLORS['disabled'])
            _carregar_reviews(id_prod)

        tree_prods.bind('<<TreeviewSelect>>', on_select_produto)

    def _dialog_avaliar_produto(self, id_produto, nome_produto,
                                nota_atual=None, comentario_atual=None,
                                callback=None):
        """Diálogo com seletor de 1-5 estrelas para avaliar um produto."""
        janela = tk.Toplevel(self.master)
        janela.title("⭐ Avaliar Produto")
        janela.geometry("420x380")
        janela.configure(bg=COLORS['bg'])
        janela.resizable(False, False)
        janela.transient(self.master)
        janela.grab_set()

        frame = tk.Frame(janela, bg=COLORS['bg'])
        frame.pack(fill='both', expand=True, padx=20, pady=20)

        tk.Label(frame, text="⭐ Avaliar Produto",
                 font=FONTS['subtitle'], fg=COLORS['primary'],
                 bg=COLORS['bg']).pack(pady=(0, 3))
        tk.Label(frame, text=nome_produto[:50],
                 font=FONTS['large'], fg=COLORS['text_primary'],
                 bg=COLORS['bg']).pack(pady=(0, 12))

        tk.Label(frame, text="Classificação *",
                 font=FONTS['normal'], fg=COLORS['text_secondary'],
                 bg=COLORS['bg']).pack(anchor='w')

        nota_var = tk.IntVar(value=nota_atual or 0)
        frame_estrelas = tk.Frame(frame, bg=COLORS['bg'])
        frame_estrelas.pack(anchor='w', pady=(5, 12))

        OPCOES = [
            (1, "★  1 — Mau"),
            (2, "★★  2 — Fraco"),
            (3, "★★★  3 — Razoável"),
            (4, "★★★★  4 — Bom"),
            (5, "★★★★★  5 — Excelente"),
        ]
        for val, texto in OPCOES:
            cor = COLORS['warning'] if val >= 4 else COLORS['text_primary']
            tk.Radiobutton(frame_estrelas, text=texto,
                          variable=nota_var, value=val,
                          font=FONTS['normal'], fg=cor,
                          bg=COLORS['bg'], activebackground=COLORS['bg'],
                          selectcolor=COLORS['bg_secondary']).pack(anchor='w')

        tk.Label(frame, text="Comentário (opcional)",
                 font=FONTS['normal'], fg=COLORS['text_secondary'],
                 bg=COLORS['bg']).pack(anchor='w')
        entry_comentario = ttk.Entry(frame, width=45, font=FONTS['normal'])
        entry_comentario.pack(fill='x', pady=(5, 10))
        if comentario_atual:
            entry_comentario.insert(0, comentario_atual)

        label_status = tk.Label(frame, text="", font=FONTS['small'], bg=COLORS['bg'])
        label_status.pack(anchor='w')

        def guardar():
            nota = nota_var.get()
            if nota == 0:
                label_status.config(text="⚠️  Selecione uma classificação.",
                                    fg=COLORS['danger'])
                return
            comentario = entry_comentario.get().strip() or None
            try:
                existe = self.db.executar_query(
                    "SELECT id_avaliacao FROM avaliacoes "
                    "WHERE id_cliente = %s AND id_produto = %s",
                    (self.usuario_atual.id_cliente, id_produto)
                )
                if existe:
                    self.db.executar_update(
                        "UPDATE avaliacoes SET nota = %s, comentario = %s "
                        "WHERE id_cliente = %s AND id_produto = %s",
                        (nota, comentario,
                         self.usuario_atual.id_cliente, id_produto)
                    )
                    logger.info("Avaliação actualizada: cliente=%s produto=%s nota=%s",
                               self.usuario_atual.id_cliente, id_produto, nota)
                else:
                    self.db.executar_update(
                        "INSERT INTO avaliacoes (id_cliente, id_produto, nota, comentario) "
                        "VALUES (%s, %s, %s, %s)",
                        (self.usuario_atual.id_cliente, id_produto, nota, comentario)
                    )
                    logger.info("Avaliação criada: cliente=%s produto=%s nota=%s",
                               self.usuario_atual.id_cliente, id_produto, nota)
                self.notify.success(f"Avaliação guardada! {'\u2605' * nota}")
                janela.destroy()
                if callback:
                    callback()
            except DatabaseError as e:
                logger.error("Erro ao guardar avaliação: %s", e)
                label_status.config(text=f"❌ Erro: {e}", fg=COLORS['danger'])

        frame_btn = tk.Frame(frame, bg=COLORS['bg'])
        frame_btn.pack(fill='x', pady=(8, 0))
        btn_g = tk.Button(frame_btn, text="✅ Guardar", command=guardar,
                         font=FONTS['normal'], bg=COLORS['success'], fg='white',
                         relief='flat', padx=25, pady=8, cursor='hand2',
                         activebackground='#059669')
        btn_g.pack(side='left', padx=5)
        btn_g.bind('<Enter>', lambda e: btn_g.config(bg='#059669'))
        btn_g.bind('<Leave>', lambda e: btn_g.config(bg=COLORS['success']))

        btn_c = tk.Button(frame_btn, text="❌ Cancelar", command=janela.destroy,
                         font=FONTS['normal'], bg=COLORS['danger'], fg='white',
                         relief='flat', padx=25, pady=8, cursor='hand2',
                         activebackground='#dc2626')
        btn_c.pack(side='left', padx=5)
        btn_c.bind('<Enter>', lambda e: btn_c.config(bg='#dc2626'))
        btn_c.bind('<Leave>', lambda e: btn_c.config(bg=COLORS['danger']))

        janela.bind('<Return>', lambda e: guardar())
        janela.bind('<Escape>', lambda e: janela.destroy())

    # ------------------------------------------------------------------
    # Logout
    # ------------------------------------------------------------------

    def fazer_logout(self):
        """Realiza logout do utilizador"""
        if self.usuario_atual:
            logger.info("Logout: %s", self.usuario_atual.email)

        self.usuario_atual = None
        self.carrinho = []
        self.cupao_ativo = None
        self.notebook = None
        self.text_carrinho = None
        self.label_cupao_status = None
        self._frame_wishlist = None
        self._frame_avaliacoes = None

        if self.db:
            self.db.desconectar()
            self.db = None

        self.mostrar_login()
