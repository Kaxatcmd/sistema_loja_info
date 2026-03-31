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
    
    def _criar_aba_explorar_produtos(self, parent):
        """Cria interface da aba de explorar produtos"""
        frame_lista = ttk.Frame(parent)
        frame_lista.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Título
        titulo = tk.Label(frame_lista, text="Produtos Disponíveis", 
                         font=FONTS['subtitle'], fg=COLORS['primary'],
                         bg=COLORS['bg'])
        titulo.pack(anchor='w', pady=(0, 10))
        
        # Container com border
        container = tk.Frame(frame_lista, bg=COLORS['bg_secondary'],
                            relief='flat', borderwidth=1,
                            highlightthickness=1,
                            highlightbackground=COLORS['border_light'])
        container.pack(fill='both', expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(container)
        scrollbar.pack(side='right', fill='y')
        
        # Listbox com estilo
        listbox = tk.Listbox(container, yscrollcommand=scrollbar.set, 
                             height=20, font=FONTS['small'],
                             bg=COLORS['bg_secondary'],
                             fg=COLORS['text_primary'],
                             selectbackground=COLORS['primary'],
                             selectforeground='white',
                             borderwidth=0)
        listbox.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.config(command=listbox.yview)
        
        # Carregar produtos
        try:
            produtos_dados = self.db.executar_query(
                "SELECT * FROM produtos WHERE stock > 0 ORDER BY nome"
            )
            produtos = [Produto.from_dict(p) for p in produtos_dados] if produtos_dados else []
        except DatabaseError as e:
            logger.error("Erro ao carregar produtos (explorar): %s", e)
            self.notify.error(f"Erro ao carregar produtos: {e}")
            produtos = []
        
        if not produtos:
            listbox.insert('end', "   Nenhum produto disponível no momento")
        else:
            for p in produtos:
                listbox.insert('end', 
                              f"  {p.nome:<35} € {p.preco:>8.2f}  │  Stock: {p.stock}")
        
        def adicionar():
            sel = listbox.curselection()
            if not sel:
                self.notify.warning("Selecione um produto!")
                return
            
            if not produtos:
                return
            
            produto = produtos[sel[0]]
            self.carrinho.append(produto)
            self.notify.success(f"'{produto.nome}' adicionado ao carrinho!")
            self._atualizar_aba_carrinho()
        
        # Frame de botões
        frame_botoes = ttk.Frame(parent)
        frame_botoes.pack(fill='x', padx=15, pady=10)
        
        btn_adicionar = tk.Button(frame_botoes, text="🛒 Adicionar ao Carrinho",
                                 command=adicionar,
                                 font=FONTS['normal'],
                                 bg=COLORS['success'],
                                 fg='white',
                                 relief='flat',
                                 padx=20, pady=10,
                                 cursor='hand2',
                                 activebackground='#059669')
        btn_adicionar.pack(side='left', padx=5)
    
    def _criar_aba_carrinho(self, parent):
        """Cria interface da aba de carrinho"""
        # Título
        titulo = tk.Label(parent, text="Itens no Carrinho", 
                         font=FONTS['subtitle'], fg=COLORS['primary'],
                         bg=COLORS['bg'])
        titulo.pack(anchor='w', padx=15, pady=(15, 10))
        
        # Container com border
        frame_info = tk.Frame(parent, bg=COLORS['bg_secondary'],
                            relief='flat', borderwidth=1,
                            highlightthickness=1,
                            highlightbackground=COLORS['border_light'])
        frame_info.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        self.text_carrinho = tk.Text(frame_info, height=15, width=80, 
                                     font=FONTS['mono'],
                                     bg=COLORS['bg_secondary'],
                                     fg=COLORS['text_primary'],
                                     relief='flat',
                                     borderwidth=0)
        self.text_carrinho.pack(fill='both', expand=True, padx=15, pady=15)
        
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
                                 bg=COLORS['success'],
                                 fg='white',
                                 relief='flat',
                                 padx=20, pady=10,
                                 cursor='hand2',
                                 activebackground='#059669')
        btn_finalizar.pack(side='left', padx=5)
        
        btn_limpar = tk.Button(frame_botoes, text="🗑️  Limpar Carrinho",
                              command=limpar_carrinho,
                              font=FONTS['normal'],
                              bg=COLORS['danger'],
                              fg='white',
                              relief='flat',
                              padx=20, pady=10,
                              cursor='hand2',
                              activebackground='#dc2626')
        btn_limpar.pack(side='left', padx=5)
    
    def _atualizar_aba_carrinho(self):
        """Atualiza o conteúdo da aba de carrinho"""
        if not hasattr(self, 'text_carrinho') or self.text_carrinho is None:
            return
        
        self.text_carrinho.config(state='normal')
        self.text_carrinho.delete(1.0, 'end')
        
        if not self.carrinho:
            msg = """  
  🛒 Seu carrinho está vazio
  
  Explore produtos e adicione à sua lista de compras!
  """
            self.text_carrinho.insert('end', msg)
        else:
            self.text_carrinho.insert('end', "  ITENS NO CARRINHO:\n")
            self.text_carrinho.insert('end', "  " + "="*70 + "\n\n")

            subtotal = 0.0
            for idx, item in enumerate(self.carrinho, 1):
                preco = float(item.preco) if item.preco is not None else 0.0
                self.text_carrinho.insert('end',
                    f"  {idx}. {item.nome:<40} €{preco:>10.2f}\n")
                subtotal += preco

            self.text_carrinho.insert('end', "\n  " + "="*70 + "\n")
            self.text_carrinho.insert('end', f"  Subtotal:       €{subtotal:>50.2f}\n")

            if self.cupao_ativo and self.cupao_ativo.esta_valido():
                desconto_val = self.cupao_ativo.calcular_desconto(subtotal)
                desconto_fmt = (
                    f"{self.cupao_ativo.desconto:.0f}%"
                    if self.cupao_ativo.tipo == "percentagem"
                    else f"€{self.cupao_ativo.desconto:.2f}"
                )
                self.text_carrinho.insert('end',
                    f"  Desconto ({self.cupao_ativo.codigo}, {desconto_fmt}):"
                    f"  -€{desconto_val:>44.2f}\n")
                total = max(0.0, subtotal - desconto_val)
            else:
                total = subtotal

            self.text_carrinho.insert('end', f"  TOTAL A PAGAR:  €{total:>50.2f}\n")
        
        self.text_carrinho.config(state='disabled')
    
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

        # Aba 4: Gerir Cupaões
        frame_cupoes = ttk.Frame(self.notebook)
        self.notebook.add(frame_cupoes, text="🎟️ Gerir Cupões")
        self._criar_aba_gerir_cupoes(frame_cupoes)
    
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
        """Cria aba para gerir produtos"""
        # Limpar widgets antigos
        for widget in parent.winfo_children():
            widget.destroy()
        
        # Título
        titulo = tk.Label(parent, text="Lista de Produtos", 
                         font=FONTS['subtitle'], fg=COLORS['primary'],
                         bg=COLORS['bg'])
        titulo.pack(anchor='w', padx=15, pady=(15, 10))
        
        # Container com border
        frame_content = tk.Frame(parent, bg=COLORS['bg_secondary'],
                                relief='flat', borderwidth=1,
                                highlightthickness=1,
                                highlightbackground=COLORS['border_light'])
        frame_content.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        text = tk.Text(frame_content, height=20, width=100, font=FONTS['mono'],
                      bg=COLORS['bg_secondary'],
                      fg=COLORS['text_primary'],
                      relief='flat',
                      borderwidth=0)
        text.pack(fill='both', expand=True, padx=15, pady=15)
        
        try:
            produtos_dados = self.db.executar_query("SELECT * FROM produtos ORDER BY id_produto")
            produtos = [Produto.from_dict(p) for p in produtos_dados] if produtos_dados else []
        except DatabaseError as e:
            logger.error("Erro ao carregar lista de produtos (admin): %s", e)
            self.notify.error(f"Erro ao carregar produtos: {e}")
            produtos = []
        
        text.insert('end', f"  {'ID':<5} │ {'Nome':<35} │ {'Preço':<12} │ {'Stock':<10}\n")
        text.insert('end', "  " + "="*72 + "\n")
        
        if produtos:
            for p in produtos:
                # Assinala visualmente os produtos em stock baixo
                linha = (
                    f"  {p.id_produto:<5} │ {p.nome[:33]:<35} │ €{p.preco:>9.2f}  │ {p.stock:<10}"
                )
                text.insert('end', linha + "\n")

        text.config(state='disabled')

        # --- Painel de alertas de stock baixo ---
        try:
            servico = StockService(self.db)
            em_alerta = servico.produtos_stock_baixo()
        except DatabaseError as e:
            logger.error("Erro ao verificar stock baixo (admin aba): %s", e)
            em_alerta = []

        if em_alerta:
            frame_alerta = tk.Frame(parent, bg=COLORS['warning'],
                                    highlightthickness=1,
                                    highlightbackground="#d97706")
            frame_alerta.pack(fill='x', padx=15, pady=(0, 8))

            tk.Label(frame_alerta,
                     text=f"⚠  {len(em_alerta)} produto(s) com stock baixo:",
                     font=FONTS['normal'], fg='white', bg=COLORS['warning']
                     ).pack(anchor='w', padx=10, pady=(6, 2))

            for p in em_alerta:
                tk.Label(frame_alerta,
                         text=f"   • {p.nome} — stock actual: {p.stock}",
                         font=FONTS['small'], fg='white', bg=COLORS['warning']
                         ).pack(anchor='w', padx=10)
            tk.Label(frame_alerta, text="", bg=COLORS['warning']).pack(pady=2)

        frame_botoes = tk.Frame(parent, bg=COLORS['bg'])
        frame_botoes.pack(fill='x', padx=15, pady=(0, 15))
        
        def novo_produto():
            """Abre janela para adicionar novo produto"""
            janela = tk.Toplevel(self.master)
            janela.title("➕ Novo Produto")
            janela.geometry("550x520")
            janela.configure(bg=COLORS['bg'])
            
            frame_main = tk.Frame(janela, bg=COLORS['bg'])
            frame_main.pack(fill='both', expand=True, padx=20, pady=20)
            
            titulo = tk.Label(frame_main, text="➕ Adicionar Novo Produto", 
                            font=FONTS['subtitle'], fg=COLORS['primary'],
                            bg=COLORS['bg'])
            titulo.pack(pady=(0, 20))
            
            # Nome
            lbl_nome = tk.Label(frame_main, text="📝 Nome do Produto *", 
                               font=FONTS['normal'], fg=COLORS['text_primary'],
                               bg=COLORS['bg'])
            lbl_nome.pack(anchor='w', pady=(10, 5))
            entry_nome = ttk.Entry(frame_main, width=50, font=FONTS['normal'])
            entry_nome.pack(fill='x', pady=(0, 15))
            entry_nome.focus()
            
            # Descrição
            lbl_desc = tk.Label(frame_main, text="📄 Descrição", 
                               font=FONTS['normal'], fg=COLORS['text_primary'],
                               bg=COLORS['bg'])
            lbl_desc.pack(anchor='w', pady=(10, 5))
            text_descricao = tk.Text(frame_main, height=4, width=50, font=FONTS['small'],
                                     bg=COLORS['bg_secondary'], fg=COLORS['text_primary'])
            text_descricao.pack(fill='x', pady=(0, 15))
            
            # Preço e Stock
            frame_preco_stock = tk.Frame(frame_main, bg=COLORS['bg'])
            frame_preco_stock.pack(fill='x', pady=(10, 15))
            
            lbl_preco = tk.Label(frame_preco_stock, text="💵 Preço (€) *", 
                                font=FONTS['normal'], fg=COLORS['text_primary'],
                                bg=COLORS['bg'])
            lbl_preco.pack(side='left', padx=(0, 15))
            entry_preco = ttk.Entry(frame_preco_stock, width=15, font=FONTS['normal'])
            entry_preco.pack(side='left')
            
            lbl_stock = tk.Label(frame_preco_stock, text="📦 Stock *", 
                                font=FONTS['normal'], fg=COLORS['text_primary'],
                                bg=COLORS['bg'])
            lbl_stock.pack(side='left', padx=(40, 15))
            entry_stock = ttk.Entry(frame_preco_stock, width=15, font=FONTS['normal'])
            entry_stock.pack(side='left')
            
            # Mensagem de status
            label_status = tk.Label(frame_main, text="", foreground=COLORS['danger'],
                                   bg=COLORS['bg'], font=FONTS['normal'])
            label_status.pack(anchor='w', pady=10)
            
            # Botões
            frame_botoes_form = tk.Frame(frame_main, bg=COLORS['bg'])
            frame_botoes_form.pack(fill='x', pady=20)
            
            def validar_e_guardar():
                """Valida e guarda novo produto"""
                nome = entry_nome.get().strip()
                descricao = text_descricao.get("1.0", 'end-1c').strip()
                preco_str = entry_preco.get().strip()
                stock_str = entry_stock.get().strip()
                
                # Validações
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
                
                # Inserir BD
                query = "INSERT INTO produtos (nome, descricao, preco, stock) VALUES (%s, %s, %s, %s)"
                try:
                    resultado = self.db.executar_update(query, (nome, descricao or None, preco, stock))
                    logger.info(
                        "Produto criado: '%s' — id=%s, preço=€%.2f, stock=%d",
                        nome, resultado, preco, stock
                    )
                    label_status.config(
                        text=f"✅ Produto '{nome}' adicionado! (ID: {resultado})",
                        foreground=COLORS['success']
                    )
                    self.master.after(1500, lambda: janela.destroy())
                    self._criar_aba_gerir_produtos(parent)
                except DatabaseError as e:
                    logger.error("Erro de BD ao criar produto '%s': %s", nome, e)
                    label_status.config(text=f"❌ Erro ao adicionar produto: {e}",
                                        foreground=COLORS['danger'])
            
            btn_guardar = tk.Button(frame_botoes_form, text="✅ Guardar",
                                   command=validar_e_guardar,
                                   font=FONTS['normal'],
                                   bg=COLORS['success'],
                                   fg='white',
                                   relief='flat',
                                   padx=30, pady=10,
                                   cursor='hand2',
                                   activebackground='#059669')
            btn_guardar.pack(side='left', padx=5, fill='x', expand=True)
            
            btn_cancelar = tk.Button(frame_botoes_form, text="❌ Cancelar",
                                    command=janela.destroy,
                                    font=FONTS['normal'],
                                    bg=COLORS['danger'],
                                    fg='white',
                                    relief='flat',
                                    padx=30, pady=10,
                                    cursor='hand2',
                                    activebackground='#dc2626')
            btn_cancelar.pack(side='left', padx=5, fill='x', expand=True)
            
            janela.bind('<Return>', lambda e: validar_e_guardar())
        
        btn_novo = tk.Button(frame_botoes, text="➕ Novo Produto",
                            command=novo_produto,
                            font=FONTS['normal'],
                            bg=COLORS['success'],
                            fg='white',
                            relief='flat',
                            padx=20, pady=10,
                            cursor='hand2',
                            activebackground='#059669')
        btn_novo.pack(side='left', padx=5)
        
        btn_recarregar = tk.Button(frame_botoes, text="🔄 Recarregar",
                                  command=lambda: self._criar_aba_gerir_produtos(parent),
                                  font=FONTS['normal'],
                                  bg=COLORS['info'],
                                  fg='white',
                                  relief='flat',
                                  padx=20, pady=10,
                                  cursor='hand2',
                                  activebackground='#0891b2')
        btn_recarregar.pack(side='left', padx=5)

        btn_pdf = tk.Button(frame_botoes, text="📄 Exportar PDF",
                            command=lambda: self._exportar_pdf_stock(),
                            font=FONTS['normal'],
                            bg=COLORS['success'],
                            fg='white',
                            relief='flat',
                            padx=20, pady=10,
                            cursor='hand2',
                            activebackground='#059669')
        btn_pdf.pack(side='left', padx=5)

    def _criar_aba_gerir_clientes(self, parent):
        """Cria aba para gerir clientes"""
        # Limpar widgets antigos
        for widget in parent.winfo_children():
            widget.destroy()
        
        # Título
        titulo = tk.Label(parent, text="Lista de Clientes", 
                         font=FONTS['subtitle'], fg=COLORS['primary'],
                         bg=COLORS['bg'])
        titulo.pack(anchor='w', padx=15, pady=(15, 10))
        
        # Container com border
        frame_content = tk.Frame(parent, bg=COLORS['bg_secondary'],
                                relief='flat', borderwidth=1,
                                highlightthickness=1,
                                highlightbackground=COLORS['border_light'])
        frame_content.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        text = tk.Text(frame_content, height=20, width=100, font=FONTS['mono'],
                      bg=COLORS['bg_secondary'],
                      fg=COLORS['text_primary'],
                      relief='flat',
                      borderwidth=0)
        text.pack(fill='both', expand=True, padx=15, pady=15)
        
        try:
            clientes_dados = self.db.executar_query(
                "SELECT id_cliente, nome, email, is_admin FROM clientes ORDER BY id_cliente"
            )
            clientes = [Cliente.from_dict(c) for c in clientes_dados] if clientes_dados else []
        except DatabaseError as e:
            logger.error("Erro ao carregar lista de clientes (admin): %s", e)
            self.notify.error(f"Erro ao carregar clientes: {e}")
            clientes = []
        
        text.insert('end', f"  {'ID':<5} │ {'Nome':<25} │ {'Email':<35} │ {'Admin':<10}\n")
        text.insert('end', "  " + "="*82 + "\n")
        
        if clientes:
            for c in clientes:
                admin = "👨‍💼 Sim" if c.is_admin else "👤 Não"
                text.insert('end', 
                    f"  {c.id_cliente:<5} │ {c.nome[:23]:<25} │ {c.email:<35} │ {admin:<10}\n")
        
        text.config(state='disabled')
        
        frame_botoes = tk.Frame(parent, bg=COLORS['bg'])
        frame_botoes.pack(fill='x', padx=15, pady=(0, 15))
        
        btn_recarregar = tk.Button(frame_botoes, text="🔄 Recarregar",
                                  command=lambda: self._criar_aba_gerir_clientes(parent),
                                  font=FONTS['normal'],
                                  bg=COLORS['info'],
                                  fg='white',
                                  relief='flat',
                                  padx=20, pady=10,
                                  cursor='hand2',
                                  activebackground='#0891b2')
        btn_recarregar.pack(side='left', padx=5)
    
    def _criar_aba_vendas(self, parent):
        """Cria aba para ver vendas"""
        # Limpar widgets antigos
        for widget in parent.winfo_children():
            widget.destroy()
        
        # Título
        titulo = tk.Label(parent, text="Histórico de Vendas", 
                         font=FONTS['subtitle'], fg=COLORS['primary'],
                         bg=COLORS['bg'])
        titulo.pack(anchor='w', padx=15, pady=(15, 10))
        
        # Container com border
        frame_content = tk.Frame(parent, bg=COLORS['bg_secondary'],
                                relief='flat', borderwidth=1,
                                highlightthickness=1,
                                highlightbackground=COLORS['border_light'])
        frame_content.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        text = tk.Text(frame_content, height=20, width=100, font=FONTS['mono'],
                      bg=COLORS['bg_secondary'],
                      fg=COLORS['text_primary'],
                      relief='flat',
                      borderwidth=0)
        text.pack(fill='both', expand=True, padx=15, pady=15)
        
        try:
            vendas = self.db.executar_query("""
                SELECT v.id_venda, c.nome, v.data, v.total
                FROM vendas v
                JOIN clientes c ON v.id_cliente = c.id_cliente
                ORDER BY v.data DESC, v.id_venda DESC
                LIMIT 50
            """)
        except DatabaseError as e:
            logger.error("Erro ao carregar histórico de vendas (admin): %s", e)
            self.notify.error(f"Erro ao carregar vendas: {e}")
            vendas = []
        
        text.insert('end', f"  {'ID':<8} │ {'Cliente':<25} │ {'Data':<15} │ {'Total':<15}\n")
        text.insert('end', "  " + "="*72 + "\n")
        
        if vendas:
            for v in vendas:
                text.insert('end', 
                    f"  {v['id_venda']:<8} │ {v['nome'][:23]:<25} │ {str(v['data']):<15} │ €{v['total']:>12.2f}\n")
        
        text.config(state='disabled')
        
        frame_botoes = tk.Frame(parent, bg=COLORS['bg'])
        frame_botoes.pack(fill='x', padx=15, pady=(0, 15))
        
        btn_recarregar = tk.Button(frame_botoes, text="🔄 Recarregar",
                                  command=lambda: self._criar_aba_vendas(parent),
                                  font=FONTS['normal'],
                                  bg=COLORS['info'],
                                  fg='white',
                                  relief='flat',
                                  padx=20, pady=10,
                                  cursor='hand2',
                                  activebackground='#0891b2')
        btn_recarregar.pack(side='left', padx=5)

        btn_pdf = tk.Button(frame_botoes, text="📄 Exportar PDF",
                            command=lambda: self._exportar_pdf_vendas(),
                            font=FONTS['normal'],
                            bg=COLORS['success'],
                            fg='white',
                            relief='flat',
                            padx=20, pady=10,
                            cursor='hand2',
                            activebackground='#059669')
        btn_pdf.pack(side='left', padx=5)

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
        """Cria aba de gesto de cupões (admin)."""
        for widget in parent.winfo_children():
            widget.destroy()

        tk.Label(parent, text="Cupões de Desconto",
                 font=FONTS['subtitle'], fg=COLORS['primary'],
                 bg=COLORS['bg']).pack(anchor='w', padx=15, pady=(15, 10))

        frame_content = tk.Frame(parent, bg=COLORS['bg_secondary'],
                                 relief='flat', borderwidth=1,
                                 highlightthickness=1,
                                 highlightbackground=COLORS['border_light'])
        frame_content.pack(fill='both', expand=True, padx=15, pady=(0, 15))

        text = tk.Text(frame_content, height=18, width=100, font=FONTS['mono'],
                       bg=COLORS['bg_secondary'], fg=COLORS['text_primary'],
                       relief='flat', borderwidth=0)
        text.pack(fill='both', expand=True, padx=15, pady=15)

        repo = CupaoRepository(self.db)
        try:
            cupoes = repo.listar_todos()
        except DatabaseError as e:
            logger.error("Erro ao carregar cupões: %s", e)
            self.notify.error(f"Erro ao carregar cupões: {e}")
            cupoes = []

        text.insert('end', f"  {'ID':<6} │ {'Código':<20} │ {'Desconto':<12} │ {'Tipo':<14} │ {'Validade':<12} │ Activo\n")
        text.insert('end', "  " + "="*82 + "\n")
        for c in cupoes:
            desconto_fmt = (
                f"{c.desconto:.0f}%" if c.tipo == "percentagem" else f"€{c.desconto:.2f}"
            )
            validade = str(c.data_validade) if c.data_validade else "Sem limite"
            activo = "✔ Sim" if c.ativo else "✘ Não"
            text.insert('end',
                f"  {c.id_cupao:<6} │ {c.codigo[:18]:<20} │ {desconto_fmt:<12} │ "
                f"{c.tipo:<14} │ {validade:<12} │ {activo}\n")
        text.config(state='disabled')

        # Botões
        frame_botoes = tk.Frame(parent, bg=COLORS['bg'])
        frame_botoes.pack(fill='x', padx=15, pady=(0, 15))

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
        
        if self.db:
            self.db.desconectar()
            self.db = None
        
        self.mostrar_login()
