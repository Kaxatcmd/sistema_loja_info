#!/usr/bin/env python3
"""
Sistema de Loja de Informática - Versão Tkinter com Abas
Aplicação com Tkinter, MariaDB e ttk.Notebook para interface com abas
Interface unificada sem janelas soltas
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import re
import bcrypt


class DatabaseManager:
    """Gerencia conexão com MariaDB"""
    
    def __init__(self, host='localhost', user='root', password='', database='loja_informatica'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
    
    def conectar(self):
        """Estabelece conexão"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                use_pure=True
            )
            return self.connection.is_connected()
        except Error as e:
            messagebox.showerror("Erro BD", f"Erro de conexão: {e}")
            return False
    
    def desconectar(self):
        """Fecha conexão"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def executar_query(self, query, params=None):
        """Executa SELECT"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            resultado = cursor.fetchall()
            cursor.close()
            return resultado
        except Error as e:
            messagebox.showerror("Erro Query", str(e))
            return None
    
    def executar_update(self, query, params=None):
        """Executa INSERT/UPDATE/DELETE"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            resultado = cursor.lastrowid
            cursor.close()
            return resultado
        except Error as e:
            self.connection.rollback()
            messagebox.showerror("Erro Update", str(e))
            return None


class LojaApp:
    """Aplicação Principal da Loja com Abas"""
    
    def __init__(self, master):
        self.master = master
        self.master.title("⌂ Sistema de Loja de Informática")
        self.master.geometry("1000x700")
        self.master.configure(bg='#f0f0f0')
        
        self.db = DatabaseManager()
        self.usuario_atual = None
        self.carrinho = []
        self.notebook = None
        
        if not self.db.conectar():
            messagebox.showerror("Erro", "Não conseguir conectar à base de dados!")
            master.quit()
            return
        
        self.exibir_login()
    
    def limpar_janela(self):
        """Remove todos os widgets da janela principal"""
        for widget in self.master.winfo_children():
            widget.destroy()
    
    def criar_logo_minimalista(self, parent):
        """Cria logotipo minimalista 'INFO SHOP' como background"""
        # Canvas com logo sutil
        canvas = tk.Canvas(parent, height=150, bg="#E0CF34", highlightthickness=0)
        canvas.pack(fill='x', padx=0, pady=0)
        
        # Dimensões do canvas
        w = 1000
        h = 150
        
        # Desenhar "INFO SHOP" minimalista
        # Texto principal (grande, leve)
        canvas.create_text(w/2, h/2, 
                          text="INFO SHOP", 
                          font=("Arial", 80, "bold"), 
                          fill="#165fa3", 
                          anchor="center")
        
        # Linhas decorativas minimalistas
        canvas.create_line(w/2 - 300, h - 10, w/2 + 300, h - 10, fill="#d0d0d0", width=2)
        
        # Ícone minimalista (circulos)
        circle_size = 30
        canvas.create_oval(w/2 - 350, h/2 - circle_size/2, 
                          w/2 - 350 + circle_size, h/2 + circle_size/2, 
                          outline="#18b4ac", width=2)
        canvas.create_oval(w/2 + 320, h/2 - circle_size/2, 
                          w/2 + 320 + circle_size, h/2 + circle_size/2, 
                          outline="#18b4ac", width=2)
        
        return canvas
    
    def exibir_login(self):
        """Tela de login"""
        self.limpar_janela()
        
        # Criar logotipo no topo
        self.criar_logo_minimalista(self.master)
        
        frame_principal = ttk.Frame(self.master)
        frame_principal.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Título
        ttk.Label(frame_principal, text="⌂ LOJA DE INFORMÁTICA", 
                 font=("Arial", 22, "bold")).pack(pady=20)
        
        # Frame de login
        frame_login = ttk.LabelFrame(frame_principal, text="Autenticação", padding=20)
        frame_login.pack(fill='x', padx=40, pady=20)
        
        # Email
        ttk.Label(frame_login, text="Email:", font=("Arial", 11)).pack()
        email_var = tk.StringVar()
        ttk.Entry(frame_login, textvariable=email_var, width=40, font=("Arial", 11)).pack(pady=5)
        
        # Password
        ttk.Label(frame_login, text="Password:", font=("Arial", 11)).pack()
        password_var = tk.StringVar()
        ttk.Entry(frame_login, textvariable=password_var, 
                 width=40, show="*", font=("Arial", 11)).pack(pady=5)
        
        # Botões
        frame_botoes = ttk.Frame(frame_principal)
        frame_botoes.pack(pady=20)
        
        def fazer_login():
            email = email_var.get().strip()
            password = password_var.get().strip()
            
            if not email or not password:
                messagebox.showwarning("Aviso", "Preencha todos os campos!")
                return
            
            cliente = self.db.executar_query(
                "SELECT * FROM clientes WHERE email = %s", (email,)
            )
            
            if not cliente:
                messagebox.showerror("Erro", "Email não encontrado!")
                return
            
            # Verificar password
            cliente_data = cliente[0]
            if not self.verificar_password(password, cliente_data.get('password', '')):
                messagebox.showerror("Erro", "Password incorreta!")
                return
            
            self.usuario_atual = cliente_data
            
            if cliente_data['is_admin']:
                self.criar_interface_admin()
            else:
                self.criar_interface_cliente()
        
        ttk.Button(frame_botoes, text="Entrar", 
                  command=fazer_login).pack(side='left', padx=10)
        ttk.Button(frame_botoes, text="Sair", 
                  command=self.master.quit).pack(side='left', padx=10)
    
    def verificar_password(self, password, password_hash):
        """Verifica password"""
        try:
            if not password_hash:
                return False
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except:
            return False
    
    def criar_interface_cliente(self):
        """Cria interface com abas para cliente"""
        self.limpar_janela()
        
        # Header
        frame_header = ttk.Frame(self.master)
        frame_header.pack(fill='x', padx=10, pady=10, side='top')
        
        ttk.Label(frame_header, text=f"◦ {self.usuario_atual['nome']}", 
                 font=("Arial", 14, "bold")).pack(side='left')
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
        # Listbox com produtos
        frame_lista = ttk.Frame(parent)
        frame_lista.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Label
        ttk.Label(frame_lista, text="Produtos Disponíveis:", 
                 font=("Arial", 11, "bold")).pack(anchor='w')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_lista)
        scrollbar.pack(side='right', fill='y')
        
        # Listbox
        listbox = tk.Listbox(frame_lista, yscrollcommand=scrollbar.set, 
                             height=20, font=("Arial", 10))
        listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=listbox.yview)
        
        # Carregar produtos
        produtos = self.db.executar_query(
            "SELECT * FROM produtos WHERE stock > 0 ORDER BY nome"
        )
        
        if not produtos:
            listbox.insert('end', "Nenhum produto disponível")
        else:
            for p in produtos:
                listbox.insert('end', 
                              f"{p['nome']:<35} €{p['preco']:>8.2f} (Stock: {p['stock']})")
        
        # Função para adicionar ao carrinho
        def adicionar():
            sel = listbox.curselection()
            if not sel:
                messagebox.showwarning("Aviso", "Selecione um produto!")
                return
            
            if not produtos:
                return
            
            produto = produtos[sel[0]]
            self.carrinho.append(produto)
            messagebox.showinfo("Sucesso", f"✔ {produto['nome']} adicionado ao carrinho!")
            self._atualizar_aba_carrinho()
        
        # Botão de ação
        frame_botoes = ttk.Frame(parent)
        frame_botoes.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(frame_botoes, text="⊕ Adicionar ao Carrinho", 
                  command=adicionar).pack(side='left', padx=5)
    
    def _criar_aba_carrinho(self, parent):
        """Cria interface da aba de carrinho"""
        # Frame superior com informações
        frame_info = ttk.LabelFrame(parent, text="Itens no Carrinho", padding=10)
        frame_info.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Text widget para exibir carrinho
        self.text_carrinho = tk.Text(frame_info, height=15, width=80, font=("Arial", 10))
        self.text_carrinho.pack(fill='both', expand=True)
        
        self._atualizar_aba_carrinho()
        
        # Frame de botões
        frame_botoes = ttk.Frame(parent)
        frame_botoes.pack(fill='x', padx=10, pady=10)
        
        def finalizar_compra():
            if not self.carrinho:
                messagebox.showwarning("Aviso", "Carrinho vazio!")
                return
            
            # Calcular total
            total = sum(item['preco'] for item in self.carrinho)
            
            if messagebox.askyesno("Confirmar", f"Finalizar compra? Total: €{total:.2f}"):
                # Criar venda
                id_venda = self.db.executar_update(
                    "INSERT INTO vendas (id_cliente, data, total) VALUES (%s, %s, %s)",
                    (self.usuario_atual['id_cliente'], datetime.now().date(), total)
                )
                
                if id_venda:
                    for item in self.carrinho:
                        self.db.executar_update(
                            "INSERT INTO venda_produto (id_venda, id_produto, preco, quantidade) VALUES (%s, %s, %s, %s)",
                            (id_venda, item['id_produto'], item['preco'], 1)
                        )
                        self.db.executar_update(
                            "UPDATE produtos SET stock = stock - 1 WHERE id_produto = %s",
                            (item['id_produto'],)
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
        if not hasattr(self, 'text_carrinho'):
            return
        
        self.text_carrinho.config(state='normal')
        self.text_carrinho.delete(1.0, 'end')
        
        if not self.carrinho:
            self.text_carrinho.insert('end', "Carrinho vazio")
        else:
            total = 0
            for idx, item in enumerate(self.carrinho, 1):
                self.text_carrinho.insert('end', 
                    f"{idx}. {item['nome']:<40} €{item['preco']:>8.2f}\n")
                total += item['preco']
            
            self.text_carrinho.insert('end', f"\n{'='*60}\nTOTAL: €{total:>48.2f}")
        
        self.text_carrinho.config(state='disabled')
    
    def criar_interface_admin(self):
        """Cria interface com abas para administrador"""
        self.limpar_janela()
        
        # Header
        frame_header = ttk.Frame(self.master)
        frame_header.pack(fill='x', padx=10, pady=10, side='top')
        
        ttk.Label(frame_header, text=f"▲ {self.usuario_atual['nome']} (Admin)", 
                 font=("Arial", 14, "bold")).pack(side='left')
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
        
        # Text widget
        text = tk.Text(frame_content, height=20, width=100, font=("Courier", 9))
        text.pack(fill='both', expand=True)
        
        # Carregar produtos
        produtos = self.db.executar_query("SELECT * FROM produtos ORDER BY id_produto")
        
        # Cabeçalho
        text.insert('end', f"{'ID':<5} {'Nome':<35} {'Preço':<12} {'Stock':<10}\n")
        text.insert('end', "="*62 + "\n")
        
        if produtos:
            for p in produtos:
                text.insert('end', 
                    f"{p['id_produto']:<5} {p['nome'][:33]:<35} €{p['preco']:>9.2f}  {p['stock']:<10}\n")
        
        text.config(state='disabled')
        
        # Botões
        frame_botoes = ttk.Frame(parent)
        frame_botoes.pack(fill='x', padx=10, pady=10)
        
        def novo_produto():
            """Abre janela para adicionar novo produto"""
            janela = tk.Toplevel(self.master)
            janela.title("⊕ Novo Produto")
            janela.geometry("500x450")
            janela.configure(bg='#f0f0f0')
            
            # Frame principal com padding
            frame_main = ttk.Frame(janela, padding=15)
            frame_main.pack(fill='both', expand=True)
            
            # Rótulo titulo
            ttk.Label(frame_main, text="Adicionar Novo Produto", 
                     font=("Arial", 14, "bold")).pack(pady=(0, 20))
            
            # Nome do Produto
            ttk.Label(frame_main, text="Nome do Produto:*").pack(anchor='w', pady=(5, 0))
            entry_nome = ttk.Entry(frame_main, width=50)
            entry_nome.pack(anchor='w', pady=(0, 10))
            entry_nome.focus()
            
            # Descrição
            ttk.Label(frame_main, text="Descrição:").pack(anchor='w', pady=(5, 0))
            text_descricao = tk.Text(frame_main, height=4, width=50, font=("Arial", 9))
            text_descricao.pack(anchor='w', pady=(0, 10))
            
            # Preço
            frame_preco = ttk.Frame(frame_main)
            frame_preco.pack(anchor='w', py=(10, 0), fill='x', pady=(5, 10))
            
            ttk.Label(frame_preco, text="Preço (€):*").pack(side='left', padx=(0, 10))
            entry_preco = ttk.Entry(frame_preco, width=15)
            entry_preco.pack(side='left')
            
            # Stock
            frame_stock = ttk.Frame(frame_main)
            frame_stock.pack(anchor='w', fill='x', pady=(5, 10))
            
            ttk.Label(frame_stock, text="Stock Inicial:*").pack(side='left', padx=(0, 10))
            entry_stock = ttk.Entry(frame_stock, width=15)
            entry_stock.pack(side='left')
            
            # Mensagem de status
            label_status = ttk.Label(frame_main, text="", foreground='red')
            label_status.pack(anchor='w', pady=(10, 0))
            
            # Frame dos botões
            frame_botoes_form = ttk.Frame(frame_main)
            frame_botoes_form.pack(fill='x', pady=(20, 0))
            
            def validar_e_guardar():
                """Valida os dados e guarda na BD"""
                # Validações
                nome = entry_nome.get().strip()
                descricao = text_descricao.get("1.0", 'end-1c').strip()
                preco_str = entry_preco.get().strip()
                stock_str = entry_stock.get().strip()
                
                # Validar preenchimento obrigatório
                if not nome:
                    label_status.config(text="⚠ Nome do produto é obrigatório!", foreground='red')
                    entry_nome.focus()
                    return
                
                if not preco_str:
                    label_status.config(text="⚠ Preço é obrigatório!", foreground='red')
                    entry_preco.focus()
                    return
                
                if not stock_str:
                    label_status.config(text="⚠ Stock é obrigatório!", foreground='red')
                    entry_stock.focus()
                    return
                
                # Validar formato de preço
                try:
                    preco = float(preco_str.replace(',', '.'))
                    if preco < 0:
                        raise ValueError("Preço não pode ser negativo")
                except ValueError:
                    label_status.config(text="⚠ Preço inválido! Use formato número decimal.", foreground='red')
                    entry_preco.focus()
                    return
                
                # Validar formato de stock
                try:
                    stock = int(stock_str)
                    if stock < 0:
                        raise ValueError("Stock não pode ser negativo")
                except ValueError:
                    label_status.config(text="⚠ Stock inválido! Use número inteiro.", foreground='red')
                    entry_stock.focus()
                    return
                
                # Validar comprimento do nome
                if len(nome) > 100:
                    label_status.config(text="⚠ Nome muito longo (máx. 100 caracteres)!", foreground='red')
                    return
                
                # Inserir na base de dados
                query = """
                    INSERT INTO produtos (nome, descricao, preco, stock) 
                    VALUES (%s, %s, %s, %s)
                """
                params = (nome, descricao if descricao else None, preco, stock)
                
                resultado = self.db.executar_update(query, params)
                
                if resultado:
                    label_status.config(
                        text=f"✔ Produto '{nome}' adicionado com sucesso! (ID: {resultado})", 
                        foreground='green'
                    )
                    # Limpar formulário
                    entry_nome.delete(0, 'end')
                    text_descricao.delete("1.0", 'end')
                    entry_preco.delete(0, 'end')
                    entry_stock.delete(0, 'end')
                    entry_nome.focus()
                    
                    # Fechar janela após 1.5 segundos
                    self.master.after(1500, lambda: janela.destroy())
                    # Recarregar a aba
                    self._criar_aba_gerir_produtos(parent)
                else:
                    label_status.config(text="✘ Erro ao adicionar produto! Verifique os dados.", foreground='red')
            
            # Botão Guardar
            ttk.Button(frame_botoes_form, text="✓ Guardar Produto", 
                      command=validar_e_guardar).pack(side='left', padx=5)
            
            # Botão Cancelar
            ttk.Button(frame_botoes_form, text="✕ Cancelar", 
                      command=janela.destroy).pack(side='left', padx=5)
            
            # Permitir fechar com Enter
            janela.bind('<Return>', lambda e: validar_e_guardar())
        
        ttk.Button(frame_botoes, text="⊕ Novo Produto", 
                  command=novo_produto).pack(side='left', padx=5)
        ttk.Button(frame_botoes, text="★ Recarregar", 
                  command=lambda: self._criar_aba_gerir_produtos(parent)).pack(side='left', padx=5)
    
    def _criar_aba_gerir_clientes(self, parent):
        """Cria aba para gerir clientes"""
        frame_content = ttk.LabelFrame(parent, text="Lista de Clientes", padding=10)
        frame_content.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Text widget
        text = tk.Text(frame_content, height=20, width=100, font=("Courier", 9))
        text.pack(fill='both', expand=True)
        
        # Carregar clientes
        clientes = self.db.executar_query(
            "SELECT id_cliente, nome, email, is_admin FROM clientes ORDER BY id_cliente"
        )
        
        # Cabeçalho
        text.insert('end', f"{'ID':<5} {'Nome':<25} {'Email':<35} {'Admin':<10}\n")
        text.insert('end', "="*75 + "\n")
        
        if clientes:
            for c in clientes:
                admin = "▲ Sim" if c['is_admin'] else "◦ Não"
                text.insert('end', 
                    f"{c['id_cliente']:<5} {c['nome'][:23]:<25} {c['email']:<35} {admin:<10}\n")
        
        text.config(state='disabled')
        
        # Botões
        frame_botoes = ttk.Frame(parent)
        frame_botoes.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(frame_botoes, text="★ Recarregar", 
                  command=lambda: self._criar_aba_gerir_clientes(parent)).pack(side='left', padx=5)
    
    def _criar_aba_vendas(self, parent):
        """Cria aba para ver vendas"""
        frame_content = ttk.LabelFrame(parent, text="Histórico de Vendas", padding=10)
        frame_content.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Text widget
        text = tk.Text(frame_content, height=20, width=100, font=("Courier", 9))
        text.pack(fill='both', expand=True)
        
        # Carregar vendas
        vendas = self.db.executar_query("""
            SELECT v.id_venda, c.nome, v.data, v.total 
            FROM vendas v 
            JOIN clientes c ON v.id_cliente = c.id_cliente 
            ORDER BY v.data DESC 
            LIMIT 50
        """)
        
        # Cabeçalho
        text.insert('end', f"{'ID':<8} {'Cliente':<25} {'Data':<15} {'Total':<15}\n")
        text.insert('end', "="*63 + "\n")
        
        if vendas:
            for v in vendas:
                text.insert('end', 
                    f"{v['id_venda']:<8} {v['nome'][:23]:<25} {str(v['data']):<15} €{v['total']:>12.2f}\n")
        
        text.config(state='disabled')
        
        # Botões
        frame_botoes = ttk.Frame(parent)
        frame_botoes.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(frame_botoes, text="★ Recarregar", 
                  command=lambda: self._criar_aba_vendas(parent)).pack(side='left', padx=5)
    
    def fazer_logout(self):
        """Fazer logout"""
        self.usuario_atual = None
        self.carrinho = []
        self.notebook = None
        self.exibir_login()


if __name__ == '__main__':
    root = tk.Tk()
    app = LojaApp(root)
    root.mainloop()
