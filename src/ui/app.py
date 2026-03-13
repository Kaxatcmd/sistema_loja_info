"""
Aplicação Principal - LojaApp
Interface gráfica com abas para Cliente e Administrador - Design Profissional
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
from src.config import FONTS, COLORS, WINDOW_WIDTH, WINDOW_HEIGHT, APP_TITLE
from src.database import DatabaseManager
from src.models.cliente import Cliente
from src.models.produto import Produto
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
        self.notebook = None
        self.text_carrinho = None
        
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
        self._frame_explorar_produtos = frame_produtos
        self._criar_aba_explorar_produtos(frame_produtos)
        
        # Aba 2: Ver Carrinho
        frame_carrinho = ttk.Frame(self.notebook)
        self.notebook.add(frame_carrinho, text="🛒 Meu Carrinho")
        self._criar_aba_carrinho(frame_carrinho)
        
        # Aba 3: Minhas Avaliações
        frame_avaliacoes = ttk.Frame(self.notebook)
        self.notebook.add(frame_avaliacoes, text="⭐ Minhas Avaliações")
        self._frame_avaliacoes = frame_avaliacoes
        self._criar_aba_avaliacoes(frame_avaliacoes)
    
    def _criar_aba_explorar_produtos(self, parent):
        """Cria interface da aba de explorar produtos"""
        # Limpar widgets antigos
        for widget in parent.winfo_children():
            widget.destroy()
        
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
        
        # Carregar produtos com médias de avaliação
        produtos_dados = self.db.executar_query("""
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
                listbox.insert('end',
                              f"  {p_data['nome']:<35} € {float(p_data['preco']):>8.2f}  │  Stock: {p_data['stock']}{rating_str}")
        
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
        
        def ver_detalhes():
            sel = listbox.curselection()
            if not sel:
                self.notify.warning("Selecione um produto para ver os detalhes!")
                return
            if not produtos:
                return
            produto = produtos[sel[0]]
            p_data = produtos_dados[sel[0]]
            media = p_data.get('media_avaliacao')
            num = p_data.get('num_avaliacoes', 0)
            self._mostrar_detalhes_produto(produto,
                                           float(media) if media is not None else None,
                                           int(num))
        
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
        
        btn_detalhes = tk.Button(frame_botoes, text="👁️ Ver Detalhes",
                                 command=ver_detalhes,
                                 font=FONTS['normal'],
                                 bg=COLORS['info'],
                                 fg='white',
                                 relief='flat',
                                 padx=20, pady=10,
                                 cursor='hand2',
                                 activebackground='#0891b2')
        btn_detalhes.pack(side='left', padx=5)
    
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
        
        # Frame de botões
        frame_botoes = tk.Frame(parent, bg=COLORS['bg'])
        frame_botoes.pack(fill='x', padx=15, pady=(0, 15))
        
        def finalizar_compra():
            if not self.carrinho:
                self.notify.warning("Carrinho vazio!")
                return
            
            total = sum(item.preco for item in self.carrinho)
            
            def confirmar_compra(resposta):
                if resposta:
                    id_venda = self.db.executar_update(
                        "INSERT INTO vendas (id_cliente, data, total) VALUES (%s, %s, %s)",
                        (self.usuario_atual.id_cliente, datetime.now().date(), total)
                    )
                    
                    if id_venda:
                        for item in self.carrinho:
                            self.db.executar_update(
                                "INSERT INTO venda_produto (id_venda, id_produto, preco, quantidade) VALUES (%s, %s, %s, %s)",
                                (id_venda, item.id_produto, item.preco, 1)
                            )
                            self.db.executar_update(
                                "UPDATE produtos SET stock = stock - 1 WHERE id_produto = %s",
                                (item.id_produto,)
                            )
                        
                        self.carrinho = []
                        self.notify.success(f"Compra finalizada!\nID da venda: {id_venda}\nTotal: €{total:.2f}")
                        self._atualizar_aba_carrinho()
                        # Atualizar aba de avaliações para mostrar produtos recém-comprados
                        if hasattr(self, '_frame_avaliacoes'):
                            self._criar_aba_avaliacoes(self._frame_avaliacoes)
            
            self.notify.question(f"Finalizar compra?\n\nTotal: €{total:.2f}", 
                                "Confirmar Compra",
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
            
            total = 0
            for idx, item in enumerate(self.carrinho, 1):
                self.text_carrinho.insert('end', 
                    f"  {idx}. {item.nome:<40} €{item.preco:>10.2f}\n")
                total += item.preco
            
            self.text_carrinho.insert('end', "\n  " + "="*70 + "\n")
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
        
        # Scrollbar e Listbox
        scrollbar_adm = ttk.Scrollbar(frame_content)
        scrollbar_adm.pack(side='right', fill='y')
        
        listbox_adm = tk.Listbox(frame_content, yscrollcommand=scrollbar_adm.set,
                                  height=20, font=FONTS['mono'],
                                  bg=COLORS['bg_secondary'],
                                  fg=COLORS['text_primary'],
                                  selectbackground=COLORS['primary'],
                                  selectforeground='white',
                                  borderwidth=0)
        listbox_adm.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar_adm.config(command=listbox_adm.yview)
        
        produtos_dados_adm = self.db.executar_query("""
            SELECT p.*,
                   AVG(a.estrelas) AS media_avaliacao,
                   COUNT(a.id_avaliacao) AS num_avaliacoes
            FROM produtos p
            LEFT JOIN avaliacoes a ON a.id_produto = p.id_produto
            GROUP BY p.id_produto
            ORDER BY p.id_produto
        """)
        produtos_adm = [Produto.from_dict(p) for p in produtos_dados_adm] if produtos_dados_adm else []
        
        header = f"  {'ID':<5} │ {'Nome':<28} │ {'Preço':>8} │ {'Stock':>5} │ Avaliação"
        listbox_adm.insert('end', header)
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
                listbox_adm.insert('end',
                    f"  {p_data['id_produto']:<5} │ {str(p_data['nome'])[:26]:<28} │ "
                    f"€{float(p_data['preco']):>7.2f} │ {p_data['stock']:>5} │ {rating_str}")
        
        frame_botoes = tk.Frame(parent, bg=COLORS['bg'])
        frame_botoes.pack(fill='x', padx=15, pady=(0, 15))
        
        def ver_detalhes_adm():
            sel = listbox_adm.curselection()
            # índices 0 e 1 são o cabeçalho e separador
            if not sel or sel[0] < 2:
                self.notify.warning("Selecione um produto para ver os detalhes!")
                return
            idx = sel[0] - 2
            if idx >= len(produtos_adm):
                return
            produto = produtos_adm[idx]
            p_data = produtos_dados_adm[idx]
            media = p_data.get('media_avaliacao')
            num = p_data.get('num_avaliacoes', 0)
            self._mostrar_detalhes_produto(produto,
                                           float(media) if media is not None else None,
                                           int(num))
        
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
                resultado = self.db.executar_update(query, (nome, descricao or None, preco, stock))
                
                if resultado:
                    label_status.config(
                        text=f"✅ Produto '{nome}' adicionado! (ID: {resultado})", 
                        foreground=COLORS['success']
                    )
                    self.master.after(1500, lambda: janela.destroy())
                    self._criar_aba_gerir_produtos(parent)
                else:
                    label_status.config(text="❌ Erro ao adicionar produto!", 
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
        
        btn_detalhes_adm = tk.Button(frame_botoes, text="👁️ Ver Detalhes",
                                     command=ver_detalhes_adm,
                                     font=FONTS['normal'],
                                     bg=COLORS['info'],
                                     fg='white',
                                     relief='flat',
                                     padx=20, pady=10,
                                     cursor='hand2',
                                     activebackground='#0891b2')
        btn_detalhes_adm.pack(side='left', padx=5)
        
        btn_recarregar = tk.Button(frame_botoes, text="🔄 Recarregar",
                                  command=lambda: self._criar_aba_gerir_produtos(parent),
                                  font=FONTS['normal'],
                                  bg=COLORS['primary'],
                                  fg='white',
                                  relief='flat',
                                  padx=20, pady=10,
                                  cursor='hand2',
                                  activebackground='#1d4ed8')
        btn_recarregar.pack(side='left', padx=5)
    
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
        
        clientes_dados = self.db.executar_query(
            "SELECT id_cliente, nome, email, is_admin FROM clientes ORDER BY id_cliente"
        )
        clientes = [Cliente.from_dict(c) for c in clientes_dados] if clientes_dados else []
        
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
        
        vendas = self.db.executar_query("""
            SELECT v.id_venda, c.nome, v.data, v.total 
            FROM vendas v 
            JOIN clientes c ON v.id_cliente = c.id_cliente 
            ORDER BY v.data DESC 
            LIMIT 50
        """)
        
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
    
    def _mostrar_detalhes_produto(self, produto, media_avaliacao=None, num_avaliacoes=0):
        """Abre popup com informação detalhada do produto"""
        janela = tk.Toplevel(self.master)
        janela.title(f"📦 {produto.nome}")
        janela.geometry("520x420")
        janela.configure(bg=COLORS['bg'])
        janela.resizable(False, False)
        janela.grab_set()

        # Header colorido
        frame_header = tk.Frame(janela, bg=COLORS['primary'], pady=15)
        frame_header.pack(fill='x')
        tk.Label(frame_header, text=produto.nome, font=FONTS['subtitle'],
                 fg='white', bg=COLORS['primary']).pack(padx=20)

        frame_body = tk.Frame(janela, bg=COLORS['bg'])
        frame_body.pack(fill='both', expand=True, padx=25, pady=20)

        # Preço
        tk.Label(frame_body, text=f"💵 Preço: €{produto.preco:.2f}",
                 font=FONTS['large'], fg=COLORS['success'], bg=COLORS['bg']).pack(anchor='w')

        # Stock
        tk.Label(frame_body, text=f"📦 Stock disponível: {produto.stock} unidades",
                 font=FONTS['normal'], fg=COLORS['text_secondary'], bg=COLORS['bg']).pack(anchor='w', pady=(5, 10))

        # Avaliação
        if media_avaliacao is not None:
            filled = round(media_avaliacao)
            stars = '★' * filled + '☆' * (5 - filled)
            av_text = f"⭐ Avaliação: {stars} {media_avaliacao:.1f}/5  ({num_avaliacoes} avaliação{'ões' if num_avaliacoes != 1 else ''})"
            tk.Label(frame_body, text=av_text,
                     font=FONTS['normal'], fg='#d97706', bg=COLORS['bg']).pack(anchor='w', pady=(0, 10))
        else:
            tk.Label(frame_body, text="⭐ Avaliação: ☆☆☆☆☆  (ainda sem avaliações)",
                     font=FONTS['normal'], fg=COLORS['text_secondary'], bg=COLORS['bg']).pack(anchor='w', pady=(0, 10))

        ttk.Separator(frame_body, orient='horizontal').pack(fill='x', pady=8)

        # Descrição
        tk.Label(frame_body, text="📄 Descrição:",
                 font=FONTS['normal'], fg=COLORS['text_primary'], bg=COLORS['bg']).pack(anchor='w')
        desc = produto.descricao if produto.descricao else "Sem descrição disponível."
        tk.Label(frame_body, text=desc, font=FONTS['small'],
                 fg=COLORS['text_secondary'], bg=COLORS['bg'],
                 wraplength=460, justify='left').pack(anchor='w', pady=(5, 0))

        tk.Button(janela, text="✖ Fechar", command=janela.destroy,
                  font=FONTS['normal'], bg=COLORS['danger'], fg='white',
                  relief='flat', padx=25, pady=8, cursor='hand2',
                  activebackground='#dc2626').pack(pady=15)

    def _criar_aba_avaliacoes(self, parent):
        """Cria aba para o cliente avaliar produtos que comprou"""
        for widget in parent.winfo_children():
            widget.destroy()

        tk.Label(parent, text="Avaliar Produtos Comprados",
                 font=FONTS['subtitle'], fg=COLORS['primary'],
                 bg=COLORS['bg']).pack(anchor='w', padx=15, pady=(15, 5))
        tk.Label(parent,
                 text="Produtos que adquiriu — clique em ⭐ Avaliar para deixar a sua nota",
                 font=FONTS['small'], fg=COLORS['text_secondary'],
                 bg=COLORS['bg']).pack(anchor='w', padx=15, pady=(0, 10))

        dados = self.db.executar_query("""
            SELECT DISTINCT p.id_produto, p.nome, p.descricao, p.preco,
                   a.estrelas AS minha_avaliacao
            FROM venda_produto vp
            JOIN vendas v ON vp.id_venda = v.id_venda
            JOIN produtos p ON vp.id_produto = p.id_produto
            LEFT JOIN avaliacoes a
                   ON a.id_produto = p.id_produto AND a.id_cliente = %s
            WHERE v.id_cliente = %s
            ORDER BY p.nome
        """, (self.usuario_atual.id_cliente, self.usuario_atual.id_cliente))

        if not dados:
            tk.Label(parent, text="Ainda não efetuou nenhuma compra.",
                     font=FONTS['normal'], fg=COLORS['text_secondary'],
                     bg=COLORS['bg']).pack(pady=40)
            return

        # Área com scroll
        outer = tk.Frame(parent, bg=COLORS['bg'])
        outer.pack(fill='both', expand=True, padx=15, pady=(0, 15))

        canvas = tk.Canvas(outer, bg=COLORS['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient='vertical', command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=COLORS['bg'])

        scrollable.bind('<Configure>',
                        lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=scrollable, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        for item in dados:
            card = tk.Frame(scrollable, bg=COLORS['bg_secondary'],
                            relief='flat', highlightthickness=1,
                            highlightbackground=COLORS['border_light'])
            card.pack(fill='x', pady=4, padx=2)

            tk.Label(card, text=item['nome'], font=FONTS['large'],
                     fg=COLORS['text_primary'],
                     bg=COLORS['bg_secondary']).pack(anchor='w', padx=12, pady=(10, 0))

            frame_linha = tk.Frame(card, bg=COLORS['bg_secondary'])
            frame_linha.pack(anchor='w', padx=12, pady=(4, 10))

            minha_nota = item['minha_avaliacao']
            if minha_nota:
                stars = '★' * minha_nota + '☆' * (5 - minha_nota)
                tk.Label(frame_linha, text=f"A sua avaliação: {stars}",
                         font=FONTS['normal'], fg='#d97706',
                         bg=COLORS['bg_secondary']).pack(side='left')
                btn_text = "✏️ Alterar"
            else:
                tk.Label(frame_linha, text="Ainda não avaliou este produto",
                         font=FONTS['normal'], fg=COLORS['text_secondary'],
                         bg=COLORS['bg_secondary']).pack(side='left')
                btn_text = "⭐ Avaliar"

            tk.Button(frame_linha, text=btn_text,
                      command=lambda i=item: self._mostrar_janela_avaliar(i, parent),
                      font=FONTS['small'], bg=COLORS['primary'], fg='white',
                      relief='flat', padx=10, pady=4, cursor='hand2',
                      activebackground='#1d4ed8').pack(side='left', padx=10)

    def _mostrar_janela_avaliar(self, produto_info, parent_aba):
        """Abre popup de seleção de estrelas para avaliar o produto"""
        janela = tk.Toplevel(self.master)
        janela.title(f"⭐ Avaliar — {produto_info['nome']}")
        janela.geometry("420x300")
        janela.configure(bg=COLORS['bg'])
        janela.resizable(False, False)
        janela.grab_set()

        tk.Label(janela, text="Avaliar produto:", font=FONTS['normal'],
                 fg=COLORS['text_secondary'], bg=COLORS['bg']).pack(pady=(20, 4))
        tk.Label(janela, text=produto_info['nome'], font=FONTS['subtitle'],
                 fg=COLORS['primary'], bg=COLORS['bg']).pack(pady=(0, 15))
        tk.Label(janela, text="Selecione a sua nota:", font=FONTS['normal'],
                 fg=COLORS['text_primary'], bg=COLORS['bg']).pack()

        nota_var = tk.IntVar(value=produto_info.get('minha_avaliacao') or 0)
        frame_estrelas = tk.Frame(janela, bg=COLORS['bg'])
        frame_estrelas.pack(pady=12)

        star_btns = []

        def atualizar_estrelas(valor):
            nota_var.set(valor)
            for i, b in enumerate(star_btns):
                b.config(text='★' if i < valor else '☆',
                         fg='#d97706' if i < valor else COLORS['text_secondary'])

        valor_inicial = produto_info.get('minha_avaliacao') or 0
        for i in range(1, 6):
            preenchido = i <= valor_inicial
            b = tk.Button(frame_estrelas,
                          text='★' if preenchido else '☆',
                          font=('Segoe UI', 26),
                          fg='#d97706' if preenchido else COLORS['text_secondary'],
                          bg=COLORS['bg'], relief='flat', cursor='hand2',
                          activebackground=COLORS['bg'],
                          command=lambda v=i: atualizar_estrelas(v))
            b.pack(side='left', padx=2)
            star_btns.append(b)

        lbl_status = tk.Label(janela, text="", font=FONTS['small'],
                              fg=COLORS['danger'], bg=COLORS['bg'])
        lbl_status.pack(pady=2)

        def guardar():
            nota = nota_var.get()
            if nota == 0:
                lbl_status.config(text="⚠️  Selecione pelo menos 1 estrela!")
                return

            existente = self.db.executar_query(
                "SELECT id_avaliacao FROM avaliacoes WHERE id_cliente = %s AND id_produto = %s",
                (self.usuario_atual.id_cliente, produto_info['id_produto'])
            )
            if existente:
                self.db.executar_update(
                    "UPDATE avaliacoes SET estrelas = %s WHERE id_cliente = %s AND id_produto = %s",
                    (nota, self.usuario_atual.id_cliente, produto_info['id_produto'])
                )
            else:
                self.db.executar_update(
                    "INSERT INTO avaliacoes (id_cliente, id_produto, estrelas) VALUES (%s, %s, %s)",
                    (self.usuario_atual.id_cliente, produto_info['id_produto'], nota)
                )

            palavra = 'estrela' if nota == 1 else 'estrelas'
            self.notify.success(f"Avaliação guardada! {'★' * nota} ({nota} {palavra})")
            janela.destroy()
            self._criar_aba_avaliacoes(parent_aba)
            # Atualizar a lista de produtos com a nova avaliação
            if hasattr(self, '_frame_explorar_produtos'):
                self._criar_aba_explorar_produtos(self._frame_explorar_produtos)

        frame_btns = tk.Frame(janela, bg=COLORS['bg'])
        frame_btns.pack(pady=10)

        tk.Button(frame_btns, text="✅ Guardar", command=guardar,
                  font=FONTS['normal'], bg=COLORS['success'], fg='white',
                  relief='flat', padx=20, pady=8, cursor='hand2',
                  activebackground='#059669').pack(side='left', padx=5)
        tk.Button(frame_btns, text="❌ Cancelar", command=janela.destroy,
                  font=FONTS['normal'], bg=COLORS['danger'], fg='white',
                  relief='flat', padx=20, pady=8, cursor='hand2',
                  activebackground='#dc2626').pack(side='left', padx=5)

    def fazer_logout(self):
        """Realiza logout do utilizador"""
        self.usuario_atual = None
        self.carrinho = []
        self.notebook = None
        self.text_carrinho = None
        
        if self.db:
            self.db.desconectar()
            self.db = None
        
        self.mostrar_login()
