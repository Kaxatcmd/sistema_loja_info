"""
Tela de Login
"""

import tkinter as tk
from tkinter import ttk, messagebox
from src.config import FONTS, COLORS
from src.database import DatabaseManager
from src.models.cliente import Cliente
from src.utils.security import verify_password
from src.ui.components.widgets import criar_logo_minimalista


class LoginScreen:
    """Tela de autenticação do utilizador"""
    
    def __init__(self, master, on_login_success):
        """
        Inicializa tela de login
        
        Args:
            master: Janela raiz
            on_login_success: Callback quando login bem-sucedido
        """
        self.master = master
        self.on_login_success = on_login_success
        self.db = DatabaseManager()
    
    def show(self):
        """Exibe a tela de login"""
        # Limpar janela
        for widget in self.master.winfo_children():
            widget.destroy()
        
        # Logo
        criar_logo_minimalista(self.master)
        
        frame_principal = ttk.Frame(self.master)
        frame_principal.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Título
        ttk.Label(frame_principal, text="⌂ LOJA DE INFORMÁTICA", 
                 font=FONTS['title']).pack(pady=20)
        
        # Frame de login
        frame_login = ttk.LabelFrame(frame_principal, text="Autenticação", padding=20)
        frame_login.pack(fill='x', padx=40, pady=20)
        
        # Email
        ttk.Label(frame_login, text="Email:", font=FONTS['normal']).pack()
        email_var = tk.StringVar()
        ttk.Entry(frame_login, textvariable=email_var, width=40, 
                 font=FONTS['normal']).pack(pady=5)
        
        # Password
        ttk.Label(frame_login, text="Password:", font=FONTS['normal']).pack()
        password_var = tk.StringVar()
        ttk.Entry(frame_login, textvariable=password_var, 
                 width=40, show="*", font=FONTS['normal']).pack(pady=5)
        
        # Botões
        frame_botoes = ttk.Frame(frame_principal)
        frame_botoes.pack(pady=20)
        
        def fazer_login():
            email = email_var.get().strip()
            password = password_var.get().strip()
            
            if not email or not password:
                messagebox.showwarning("Aviso", "Preencha todos os campos!")
                return
            
            if not self.db.conectar():
                messagebox.showerror("Erro", "Não conseguir conectar à BD!")
                return
            
            cliente_dados = self.db.executar_query(
                "SELECT * FROM clientes WHERE email = %s", (email,)
            )
            
            if not cliente_dados:
                messagebox.showerror("Erro", "Email não encontrado!")
                self.db.desconectar()
                return
            
            cliente = Cliente.from_dict(cliente_dados[0])
            if not verify_password(password, cliente.password):
                messagebox.showerror("Erro", "Password incorreta!")
                self.db.desconectar()
                return
            
            # Login bem-sucedido
            self.on_login_success(cliente, self.db)
        
        ttk.Button(frame_botoes, text="Entrar", 
                  command=fazer_login).pack(side='left', padx=10)
        ttk.Button(frame_botoes, text="Sair", 
                  command=self.master.quit).pack(side='left', padx=10)
        
        # Permitir Enter para login
        self.master.bind('<Return>', lambda e: fazer_login())
