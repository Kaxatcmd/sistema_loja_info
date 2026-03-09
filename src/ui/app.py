"""
Aplicação Principal - LojaApp
Interface gráfica com abas para Cliente e Administrador
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from src.config import FONTS, COLORS, WINDOW_WIDTH, WINDOW_HEIGHT, APP_TITLE
from src.database import DatabaseManager
from src.models.cliente import Cliente
from src.models.produto import Produto
from src.utils.validators import validar_nome_produto, validar_preco, validar_stock
from src.ui.screens.login import LoginScreen


class LojaApp:
    """Aplicação Principal da Loja com Interface em Abas"""
    
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
        
        self.db = None
        self.usuario_atual = None
        self.carrinho = []
        self.notebook = None
        self.text_carrinho = None
        
        # Mostrar login
        self.mostrar_login()
    
    def mostrar_login(self):
        """Exibe tela de login"""
        login = LoginScreen(self.master, self.on_login_success)
        login.show()
    
    def on_login_success(self, usuario_cliente, db):
        """
        Callback executado após login bem-sucedido
        
        Args:
            usuario_cliente (Cliente): Objeto do utilizador autenticado
            db (DatabaseManager): Gerenciador de BD
        """
        self.usuario_atual = usuario_cliente
        self.db = db
        
        if usuario_cliente.is_admin:
            self.criar_interface_admin()
        else:
            self.criar_interface_cliente()
    
    def limpar_janela(self):
        """Remove todos os widgets da janela principal"""
        for widget in self.master.winfo_children():
            widget.destroy()
    
    def criar_interface_cliente(self):
        """Cria interface com abas para cliente"""
        self.limpar_janela()
        
        # Header
        frame_header = ttk.Frame(self.master)
        frame_header.pack(fill='x', padx=10, pady=10, side='top')
        
        ttk.Label(frame_header, text=f"◦ {self.usuario_atual.nome}", 
                 font=FONTS['large']).pack(side='left')
        ttk.Button(frame_header, text="◆ Logout", 
                  command=self.fazer_logout).pack(side='right', padx=5)
        
        # Notebook (abas)
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Aba 1: Explorar Produtos
        frame_produtos = ttk.Frame(self.notebook)
        self.notebook.add(frame_produtos, text="▸ Explorar Produtos")
        self._criar_aba_explorar_produtos(frame_produtos)
        
        # Aba 2: Ver Carrinho
        frame_carrinho = ttk.Frame(self.notebook)
        self.notebook.add(frame_carrinho, text="▪ Ver Carrinho")
        self._criar_aba_carrinho(frame_carrinho)
    
    def _criar_aba_explorar_produtos(self, parent):
        """Cria interface da aba de explorar produtos"""
        frame_lista = ttk.Frame(parent)
        frame_lista.pack(fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(frame_lista, text="Produtos Disponíveis:", 
                 font=FONTS['normal']).pack(anchor='w')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_lista)
        scrollbar.pack(side='right', fill='y')
        
        # Listbox
        listbox = tk.Listbox(frame_lista, yscrollcommand=scrollbar.set, 
                             height=20, font=FONTS['small'])
        listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=listbox.yview)
        
        # Carregar produtos
        produtos_dados = self.db.executar_query(
            "SELECT * FROM produtos WHERE stock > 0 ORDER BY nome"
        )
        
        produtos = [Produto.from_dict(p) for p in produtos_dados] if produtos_dados else []
        
        if not produtos:
            listbox.insert('end', "Nenhum produto disponível")
        else:
            for p in produtos:
                listbox.insert('end', 
                              f"{p.nome:<35} €{p.preco:>8.2f} (Stock: {p.stock})")
        
        def adicionar():
            sel = listbox.curselection()
            if not sel:
                messagebox.showwarning("Aviso", "Selecione um produto!")
                return
            
            if not produtos:
                return
            
            produto = produtos[sel[0]]
            self.carrinho.append(produto)
            messagebox.showinfo("Sucesso", f"✔ {produto.nome} adicionado ao carrinho!")
            self._atualizar_aba_carrinho()
        
        # Frame de botões
        frame_botoes = ttk.Frame(parent)
        frame_botoes.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(frame_botoes, text="⊕ Adicionar ao Carrinho", 
                  command=adicionar).pack(side='left', padx=5)
    
    def _criar_aba_carrinho(self, parent):
        """Cria interface da aba de carrinho"""
        frame_info = ttk.LabelFrame(parent, text="Itens no Carrinho", padding=10)
        frame_info.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.text_carrinho = tk.Text(frame_info, height=15, width=80, font=FONTS['mono'])
        self.text_carrinho.pack(fill='both', expand=True)
        
        self._atualizar_aba_carrinho()
        
        # Frame de botões
        frame_botoes = ttk.Frame(parent)
        frame_botoes.pack(fill='x', padx=10, pady=10)
        
        def finalizar_compra():
            if not self.carrinho:
                messagebox.showwarning("Aviso", "Carrinho vazio!")
                return
            
            total = sum(item.preco for item in self.carrinho)
            
            if messagebox.askyesno("Confirmar", f"Finalizar compra? Total: €{total:.2f}"):
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
                    messagebox.showinfo("Sucesso", f"✔ Compra finalizada!\nID da venda: {id_venda}\nTotal: €{total:.2f}")
                    self._atualizar_aba_carrinho()
        
        def limpar_carrinho():
            if self.carrinho:
                if messagebox.askyesno("Confirmar", "Limpar carrinho?"):
                    self.carrinho = []
                    self._atualizar_aba_carrinho()
        
        ttk.Button(frame_botoes, text="✔ Finalizar Compra", 
                  command=finalizar_compra).pack(side='left', padx=5)
        ttk.Button(frame_botoes, text="✘ Limpar Carrinho", 
                  command=limpar_carrinho).pack(side='left', padx=5)
    
    def _atualizar_aba_carrinho(self):
        """Atualiza o conteúdo da aba de carrinho"""
        if not hasattr(self, 'text_carrinho') or self.text_carrinho is None:
            return
        
        self.text_carrinho.config(state='normal')
        self.text_carrinho.delete(1.0, 'end')
        
        if not self.carrinho:
            self.text_carrinho.insert('end', "Carrinho vazio")
        else:
            total = 0
            for idx, item in enumerate(self.carrinho, 1):
                self.text_carrinho.insert('end', 
                    f"{idx}. {item.nome:<40} €{item.preco:>8.2f}\n")
                total += item.preco
            
            self.text_carrinho.insert('end', f"\n{'='*60}\nTOTAL: €{total:>48.2f}")
        
        self.text_carrinho.config(state='disabled')
    
    def criar_interface_admin(self):
        """Cria interface com abas para administrador"""
        self.limpar_janela()
        
        # Header
        frame_header = ttk.Frame(self.master)
        frame_header.pack(fill='x', padx=10, pady=10, side='top')
        
        ttk.Label(frame_header, text=f"▲ {self.usuario_atual.nome} (Admin)", 
                 font=FONTS['large']).pack(side='left')
        ttk.Button(frame_header, text="◆ Logout", 
                  command=self.fazer_logout).pack(side='right', padx=5)
        
        # Notebook (abas)
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Aba 1: Gerir Produtos
        frame_produtos = ttk.Frame(self.notebook)
        self.notebook.add(frame_produtos, text="▬ Gerir Produtos")
        self._criar_aba_gerir_produtos(frame_produtos)
        
        # Aba 2: Gerir Clientes
        frame_clientes = ttk.Frame(self.notebook)
        self.notebook.add(frame_clientes, text="◩ Gerir Clientes")
        self._criar_aba_gerir_clientes(frame_clientes)
        
        # Aba 3: Ver Vendas
        frame_vendas = ttk.Frame(self.notebook)
        self.notebook.add(frame_vendas, text="▣ Ver Vendas")
        self._criar_aba_vendas(frame_vendas)
    
    def _criar_aba_gerir_produtos(self, parent):
        """Cria aba para gerir produtos"""
        frame_content = ttk.LabelFrame(parent, text="Lista de Produtos", padding=10)
        frame_content.pack(fill='both', expand=True, padx=10, pady=10)
        
        text = tk.Text(frame_content, height=20, width=100, font=FONTS['mono'])
        text.pack(fill='both', expand=True)
        
        produtos_dados = self.db.executar_query("SELECT * FROM produtos ORDER BY id_produto")
        produtos = [Produto.from_dict(p) for p in produtos_dados] if produtos_dados else []
        
        text.insert('end', f"{'ID':<5} {'Nome':<35} {'Preço':<12} {'Stock':<10}\n")
        text.insert('end', "="*62 + "\n")
        
        if produtos:
            for p in produtos:
                text.insert('end', 
                    f"{p.id_produto:<5} {p.nome[:33]:<35} €{p.preco:>9.2f}  {p.stock:<10}\n")
        
        text.config(state='disabled')
        
        frame_botoes = ttk.Frame(parent)
        frame_botoes.pack(fill='x', padx=10, pady=10)
        
        def novo_produto():
            """Abre janela para adicionar novo produto"""
            janela = tk.Toplevel(self.master)
            janela.title("⊕ Novo Produto")
            janela.geometry("500x450")
            janela.configure(bg=COLORS['bg'])
            
            frame_main = ttk.Frame(janela, padding=15)
            frame_main.pack(fill='both', expand=True)
            
            ttk.Label(frame_main, text="Adicionar Novo Produto", 
                     font=FONTS['large']).pack(pady=(0, 20))
            
            ttk.Label(frame_main, text="Nome do Produto:*").pack(anchor='w', pady=(5, 0))
            entry_nome = ttk.Entry(frame_main, width=50)
            entry_nome.pack(anchor='w', pady=(0, 10))
            entry_nome.focus()
            
            ttk.Label(frame_main, text="Descrição:").pack(anchor='w', pady=(5, 0))
            text_descricao = tk.Text(frame_main, height=4, width=50, font=FONTS['small'])
            text_descricao.pack(anchor='w', pady=(0, 10))
            
            frame_preco = ttk.Frame(frame_main)
            frame_preco.pack(anchor='w', fill='x', pady=(5, 10))
            
            ttk.Label(frame_preco, text="Preço (€):*").pack(side='left', padx=(0, 10))
            entry_preco = ttk.Entry(frame_preco, width=15)
            entry_preco.pack(side='left')
            
            frame_stock = ttk.Frame(frame_main)
            frame_stock.pack(anchor='w', fill='x', pady=(5, 10))
            
            ttk.Label(frame_stock, text="Stock Inicial:*").pack(side='left', padx=(0, 10))
            entry_stock = ttk.Entry(frame_stock, width=15)
            entry_stock.pack(side='left')
            
            label_status = ttk.Label(frame_main, text="", foreground='red')
            label_status.pack(anchor='w', pady=(10, 0))
            
            frame_botoes_form = ttk.Frame(frame_main)
            frame_botoes_form.pack(fill='x', pady=(20, 0))
            
            def validar_e_guardar():
                """Valida e guarda novo produto"""
                nome = entry_nome.get().strip()
                descricao = text_descricao.get("1.0", 'end-1c').strip()
                preco_str = entry_preco.get().strip()
                stock_str = entry_stock.get().strip()
                
                # Validações
                valido, msg = validar_nome_produto(nome)
                if not valido:
                    label_status.config(text=f"⚠ {msg}", foreground='red')
                    entry_nome.focus()
                    return
                
                valido, preco, msg = validar_preco(preco_str)
                if not valido:
                    label_status.config(text=f"⚠ {msg}", foreground='red')
                    entry_preco.focus()
                    return
                
                valido, stock, msg = validar_stock(stock_str)
                if not valido:
                    label_status.config(text=f"⚠ {msg}", foreground='red')
                    entry_stock.focus()
                    return
                
                # Inserir BD
                query = "INSERT INTO produtos (nome, descricao, preco, stock) VALUES (%s, %s, %s, %s)"
                resultado = self.db.executar_update(query, (nome, descricao or None, preco, stock))
                
                if resultado:
                    label_status.config(
                        text=f"✔ Produto '{nome}' adicionado! (ID: {resultado})", 
                        foreground='green'
                    )
                    self.master.after(1500, lambda: janela.destroy())
                    self._criar_aba_gerir_produtos(parent)
                else:
                    label_status.config(text="✘ Erro ao adicionar produto!", foreground='red')
            
            ttk.Button(frame_botoes_form, text="✓ Guardar Produto", 
                      command=validar_e_guardar).pack(side='left', padx=5)
            ttk.Button(frame_botoes_form, text="✕ Cancelar", 
                      command=janela.destroy).pack(side='left', padx=5)
            
            janela.bind('<Return>', lambda e: validar_e_guardar())
        
        ttk.Button(frame_botoes, text="⊕ Novo Produto", 
                  command=novo_produto).pack(side='left', padx=5)
        ttk.Button(frame_botoes, text="★ Recarregar", 
                  command=lambda: self._criar_aba_gerir_produtos(parent)).pack(side='left', padx=5)
    
    def _criar_aba_gerir_clientes(self, parent):
        """Cria aba para gerir clientes"""
        frame_content = ttk.LabelFrame(parent, text="Lista de Clientes", padding=10)
        frame_content.pack(fill='both', expand=True, padx=10, pady=10)
        
        text = tk.Text(frame_content, height=20, width=100, font=FONTS['mono'])
        text.pack(fill='both', expand=True)
        
        clientes_dados = self.db.executar_query(
            "SELECT id_cliente, nome, email, is_admin FROM clientes ORDER BY id_cliente"
        )
        clientes = [Cliente.from_dict(c) for c in clientes_dados] if clientes_dados else []
        
        text.insert('end', f"{'ID':<5} {'Nome':<25} {'Email':<35} {'Admin':<10}\n")
        text.insert('end', "="*75 + "\n")
        
        if clientes:
            for c in clientes:
                admin = "▲ Sim" if c.is_admin else "◦ Não"
                text.insert('end', 
                    f"{c.id_cliente:<5} {c.nome[:23]:<25} {c.email:<35} {admin:<10}\n")
        
        text.config(state='disabled')
        
        frame_botoes = ttk.Frame(parent)
        frame_botoes.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(frame_botoes, text="★ Recarregar", 
                  command=lambda: self._criar_aba_gerir_clientes(parent)).pack(side='left', padx=5)
    
    def _criar_aba_vendas(self, parent):
        """Cria aba para ver vendas"""
        frame_content = ttk.LabelFrame(parent, text="Histórico de Vendas", padding=10)
        frame_content.pack(fill='both', expand=True, padx=10, pady=10)
        
        text = tk.Text(frame_content, height=20, width=100, font=FONTS['mono'])
        text.pack(fill='both', expand=True)
        
        vendas = self.db.executar_query("""
            SELECT v.id_venda, c.nome, v.data, v.total 
            FROM vendas v 
            JOIN clientes c ON v.id_cliente = c.id_cliente 
            ORDER BY v.data DESC 
            LIMIT 50
        """)
        
        text.insert('end', f"{'ID':<8} {'Cliente':<25} {'Data':<15} {'Total':<15}\n")
        text.insert('end', "="*63 + "\n")
        
        if vendas:
            for v in vendas:
                text.insert('end', 
                    f"{v['id_venda']:<8} {v['nome'][:23]:<25} {str(v['data']):<15} €{v['total']:>12.2f}\n")
        
        text.config(state='disabled')
        
        frame_botoes = ttk.Frame(parent)
        frame_botoes.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(frame_botoes, text="★ Recarregar", 
                  command=lambda: self._criar_aba_vendas(parent)).pack(side='left', padx=5)
    
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
