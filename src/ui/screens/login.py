"""
Tela de Login - Design Profissional
"""

import tkinter as tk
from src.config import FONTS, COLORS, WINDOW_WIDTH
from src.database import DatabaseManager
from src.models.cliente import Cliente
from src.utils.security import verify_password
from src.ui.components.widgets import criar_logo_minimalista
from src.ui.theme import ModernStyle, criar_botao_primario, criar_botao_secundario, ModernEntry


class LoginScreen:
    """Tela de autenticação do utilizador com design moderno"""
    
    def __init__(self, master, on_login_success, on_register_click, notify):
        """
        Inicializa tela de login
        
        Args:
            master: Janela raiz
            on_login_success: Callback quando login bem-sucedido
            on_register_click: Callback quando clicar em "Registe-se aqui"
            notify: NotificationManager do LojaApp
        """
        self.master = master
        self.on_login_success = on_login_success
        self.on_register_click = on_register_click
        self.db = DatabaseManager()
        self.notify = notify
        ModernStyle.configurar_temas()
    
    def show(self):
        """Exibe a tela de login com design profissional"""
        # Limpar janela (exceto notification_frame)
        for widget in self.master.winfo_children():
            if widget != self.notify.notification_frame:
                widget.destroy()
        
        # Definir cor de fundo
        self.master.configure(bg=COLORS['bg'])
        
        # Logo elegante
        criar_logo_minimalista(self.master)
        
        # Container principal centralizado
        container_externo = tk.Frame(self.master, bg=COLORS['bg'])
        container_externo.pack(expand=True, fill='both', padx=20, pady=10)
        
        # Frame central
        frame_central = tk.Frame(container_externo, bg=COLORS['bg_secondary'],
                                relief='flat', borderwidth=2,
                                highlightthickness=2,
                                highlightbackground=COLORS['border_light'])
        frame_central.pack(expand=True, padx=50, pady=10, fill='x', ipadx=30, ipady=15)
        
        # Título
        lbl_titulo = tk.Label(frame_central, text="Bem-vindo ao Sistema", 
                             font=FONTS['title'], fg=COLORS['primary'],
                             bg=COLORS['bg_secondary'])
        lbl_titulo.pack(pady=(0, 5))
        
        # Subtítulo
        lbl_subtitulo = tk.Label(frame_central, 
                                text="Aceda ao seu painel de controlo", 
                                font=FONTS['normal'], fg=COLORS['text_secondary'],
                                bg=COLORS['bg_secondary'])
        lbl_subtitulo.pack(pady=(0, 20))
        
        # === FORMULÁRIO DE LOGIN ===
        form_frame = tk.Frame(frame_central, bg=COLORS['bg_secondary'])
        form_frame.pack(fill='x', padx=20, pady=10)
        
        # Email
        lbl_email = tk.Label(form_frame, text="📧 Email", 
                            font=FONTS['normal'], fg=COLORS['text_primary'],
                            bg=COLORS['bg_secondary'])
        lbl_email.pack(anchor='w', pady=(0, 5))
        
        email_var = tk.StringVar()
        entry_email = ModernEntry(form_frame, placeholder="seu@email.com",
                                 textvariable=email_var, width=40)
        entry_email.pack(fill='x', pady=(0, 12))
        
        # Password
        lbl_password = tk.Label(form_frame, text="🔐 Palavra-passe", 
                               font=FONTS['normal'], fg=COLORS['text_primary'],
                               bg=COLORS['bg_secondary'])
        lbl_password.pack(anchor='w', pady=(0, 5))
        
        password_var = tk.StringVar()
        entry_password = ModernEntry(form_frame, textvariable=password_var,
                         width=40, show="●")
        entry_password.pack(fill='x', pady=(0, 15))
        
        # Informação de ajuda
        lbl_ajuda = tk.Label(form_frame, 
                            text="💡 Use as credenciais fornecidas para aceder",
                            font=FONTS['small'], fg=COLORS['text_secondary'],
                            bg=COLORS['bg_secondary'])
        lbl_ajuda.pack(anchor='w', pady=(0, 18))
        
        # === BOTÕES ===
        frame_botoes = tk.Frame(frame_central, bg=COLORS['bg_secondary'])
        frame_botoes.pack(fill='x', padx=20, pady=(5, 10))
        
        def fazer_login():
            """Realiza o login"""
            email = email_var.get().strip()
            password = password_var.get().strip()
            
            if not email or not password:
                self.notify.warning("Por favor, preencha todos os campos!")
                return
            
            # Simular conexão
            if not self.db.conectar():
                self.notify.error("Não foi possível conectar à base de dados!")
                return
            
            try:
                cliente_dados = self.db.executar_query(
                    "SELECT * FROM clientes WHERE email = %s", (email,)
                )
                
                if not cliente_dados:
                    self.notify.error("Email não encontrado!")
                    self.db.desconectar()
                    return
                
                cliente = Cliente.from_dict(cliente_dados[0])
                if not verify_password(password, cliente.password):
                    self.notify.error("Palavra-passe incorreta!")
                    self.db.desconectar()
                    return
                
                # Login bem-sucedido
                self.on_login_success(cliente, self.db)
                
            except Exception as e:
                self.notify.error(f"Erro ao fazer login: {str(e)}")
                self.db.desconectar()
        
        # Botão Entrar
        btn_entrar = tk.Button(frame_botoes, text="🔓 Entrar",
                              command=fazer_login,
                              font=FONTS['normal'],
                              bg=COLORS['primary'],
                              fg='white',
                              relief='flat',
                              padx=20, pady=8,
                              cursor='hand2',
                              activebackground=COLORS['primary_light'])
        btn_entrar.pack(side='left', padx=10, fill='x', expand=True)
        
        # Botão Sair
        btn_sair = tk.Button(frame_botoes, text="❌ Sair",
                            command=self.master.quit,
                            font=FONTS['normal'],
                            bg=COLORS['danger'],
                            fg='white',
                            relief='flat',
                            padx=20, pady=8,
                            cursor='hand2',
                            activebackground='#dc2626')
        btn_sair.pack(side='left', padx=10, fill='x', expand=True)
        
        # Link de Registo
        frame_registo = tk.Frame(frame_central, bg=COLORS['bg_secondary'])
        frame_registo.pack(fill='x', padx=20, pady=(0, 0))
        
        lbl_registo_texto = tk.Label(frame_registo, 
                                     text="Caso não possua conta, ",
                                     font=FONTS['normal'], 
                                     fg=COLORS['text_secondary'],
                                     bg=COLORS['bg_secondary'])
        lbl_registo_texto.pack(side='left')
        
        link_registo = tk.Label(frame_registo, 
                               text="registe-se aqui",
                               font=(FONTS['normal'][0], FONTS['normal'][1], 'underline'),
                               fg=COLORS['primary'],
                               bg=COLORS['bg_secondary'],
                               cursor='hand2')
        link_registo.pack(side='left')
        
        # Evento de clique no link
        link_registo.bind('<Button-1>', lambda e: self.on_register_click())
        
        # Permitir Enter para login
        self.master.bind('<Return>', lambda e: fazer_login())
        
        # Focar no campo de email
        entry_email.focus()

