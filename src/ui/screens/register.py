"""
Tela de Registo - Design Profissional
"""

import tkinter as tk
from src.config import FONTS, COLORS, WINDOW_WIDTH
from src.database import DatabaseManager
from src.utils.security import hash_password
from src.utils.validators import validar_email, validar_password
from src.ui.components.widgets import criar_logo_minimalista
from src.ui.theme import ModernStyle, ModernEntry


class RegisterScreen:
    """Tela de registo de novo utilizador com design moderno"""
    
    def __init__(self, master, on_register_success, on_back_to_login, notify):
        """
        Inicializa tela de registo
        
        Args:
            master: Janela raiz
            on_register_success: Callback quando registo bem-sucedido
            on_back_to_login: Callback para voltar ao login
            notify: NotificationManager do LojaApp
        """
        self.master = master
        self.on_register_success = on_register_success
        self.on_back_to_login = on_back_to_login
        self.db = DatabaseManager()
        self.notify = notify
        ModernStyle.configurar_temas()
    
    def show(self):
        """Exibe a tela de registo com design profissional"""
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
        container_externo.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Frame central
        frame_central = tk.Frame(container_externo, bg=COLORS['bg_secondary'],
                                relief='flat', borderwidth=2,
                                highlightthickness=2,
                                highlightbackground=COLORS['border_light'])
        frame_central.pack(expand=True, padx=50, pady=20, fill='x', ipadx=40, ipady=30)
        
        # Título
        lbl_titulo = tk.Label(frame_central, text="Criar Nova Conta", 
                             font=FONTS['title'], fg=COLORS['primary'],
                             bg=COLORS['bg_secondary'])
        lbl_titulo.pack(pady=(0, 5))
        
        # Subtítulo
        lbl_subtitulo = tk.Label(frame_central, 
                                text="Preencha os campos abaixo para se registar", 
                                font=FONTS['normal'], fg=COLORS['text_secondary'],
                                bg=COLORS['bg_secondary'])
        lbl_subtitulo.pack(pady=(0, 30))
        
        # === CANVAS COM SCROLL ===
        canvas = tk.Canvas(frame_central, bg=COLORS['bg_secondary'], 
                          highlightthickness=0, height=400)
        scrollbar = tk.Scrollbar(frame_central, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS['bg_secondary'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas e scrollbar
        canvas.pack(side='left', fill='both', expand=True, padx=20, pady=20)
        scrollbar.pack(side='right', fill='y', padx=(0, 20), pady=20)
        
        # Permitir scroll com mouse wheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # === FORMULÁRIO DE REGISTO ===
        form_frame = scrollable_frame
        
        # Nome
        lbl_nome = tk.Label(form_frame, text="👤 Nome Completo", 
                           font=FONTS['normal'], fg=COLORS['text_primary'],
                           bg=COLORS['bg_secondary'])
        lbl_nome.pack(anchor='w', pady=(0, 5))
        
        entry_nome = ModernEntry(form_frame, placeholder="Seu nome completo",
                                width=40)
        entry_nome.pack(fill='x', pady=(0, 20))
        
        # Email
        lbl_email = tk.Label(form_frame, text="📧 Email", 
                            font=FONTS['normal'], fg=COLORS['text_primary'],
                            bg=COLORS['bg_secondary'])
        lbl_email.pack(anchor='w', pady=(0, 5))
        
        entry_email = ModernEntry(form_frame, placeholder="seu@email.com",
                                 width=40)
        entry_email.pack(fill='x', pady=(0, 20))
        
        # Telefone
        lbl_telefone = tk.Label(form_frame, text="📞 Telefone (Opcional)", 
                               font=FONTS['normal'], fg=COLORS['text_primary'],
                               bg=COLORS['bg_secondary'])
        lbl_telefone.pack(anchor='w', pady=(0, 5))
        
        entry_telefone = ModernEntry(form_frame, placeholder="912345678",
                                    width=40)
        entry_telefone.pack(fill='x', pady=(0, 20))
        
        # Password
        lbl_password = tk.Label(form_frame, text="🔐 Palavra-passe", 
                               font=FONTS['normal'], fg=COLORS['text_primary'],
                               bg=COLORS['bg_secondary'])
        lbl_password.pack(anchor='w', pady=(0, 5))
        
        password_var = tk.StringVar()
        entry_password = tk.Entry(form_frame, textvariable=password_var,
                                 show="●", font=FONTS['normal'],
                                 bg=COLORS['bg'], fg=COLORS['text_primary'],
                                 relief='solid', borderwidth=1,
                                 insertbackground=COLORS['primary'])
        entry_password.pack(fill='x', pady=(0, 20))
        
        # Confirmar Password
        lbl_password_confirm = tk.Label(form_frame, text="🔐 Confirmar Palavra-passe", 
                                       font=FONTS['normal'], fg=COLORS['text_primary'],
                                       bg=COLORS['bg_secondary'])
        lbl_password_confirm.pack(anchor='w', pady=(0, 5))
        
        password_confirm_var = tk.StringVar()
        entry_password_confirm = tk.Entry(form_frame, textvariable=password_confirm_var,
                                         show="●", font=FONTS['normal'],
                                         bg=COLORS['bg'], fg=COLORS['text_primary'],
                                         relief='solid', borderwidth=1,
                                         insertbackground=COLORS['primary'])
        entry_password_confirm.pack(fill='x', pady=(0, 25))
        
        # Informação de ajuda
        lbl_ajuda = tk.Label(form_frame, 
                            text="💡 Palavra-passe deve ter pelo menos 6 caracteres",
                            font=FONTS['small'], fg=COLORS['text_secondary'],
                            bg=COLORS['bg_secondary'])
        lbl_ajuda.pack(anchor='w', pady=(0, 30))
        
        # === BOTÕES (fora do scroll) ===
        frame_botoes = tk.Frame(frame_central, bg=COLORS['bg_secondary'])
        frame_botoes.pack(fill='x', padx=20, pady=20)
        
        def fazer_registo():
            """Realiza o registo de novo utilizador"""
            nome = entry_nome.get_value().strip()
            email = entry_email.get_value().strip()
            telefone = entry_telefone.get_value().strip()
            password = password_var.get().strip()
            password_confirm = password_confirm_var.get().strip()
            
            # Validações
            if not nome:
                self.notify.warning("Por favor, preencha o nome!")
                return
            
            if not email:
                self.notify.warning("Por favor, preencha o email!")
                return
            
            # Validar email formato
            email_valido, msg_email = validar_email(email)
            if not email_valido:
                self.notify.warning(msg_email)
                return
            
            # Validar password
            password_valida, msg_password = validar_password(password)
            if not password_valida:
                self.notify.warning(msg_password)
                return
            
            # Validar confirmação de password
            if password != password_confirm:
                self.notify.warning("As palavras-passe não correspondem!")
                return
            
            # Conectar BD
            if not self.db.conectar():
                self.notify.error("Não foi possível conectar à base de dados!")
                return
            
            try:
                # Verificar se email já existe
                cliente_existente = self.db.executar_query(
                    "SELECT * FROM clientes WHERE email = %s", (email,)
                )
                
                if cliente_existente:
                    self.notify.error("Este email já está registado no sistema!")
                    self.db.desconectar()
                    return
                
                # Hash da password
                password_hash = hash_password(password)
                
                # Inserir novo cliente (is_admin = 0 por defeito)
                resultado = self.db.executar_update(
                    "INSERT INTO clientes (nome, email, telefone, password, is_admin) VALUES (%s, %s, %s, %s, 0)",
                    (nome, email, telefone if telefone else None, password_hash)
                )
                
                if resultado:
                    self.notify.success("Conta criada com sucesso! Redirecionando para login...")
                    self.master.after(1500, self.on_back_to_login)
                else:
                    self.notify.error("Erro ao criar a conta. Tente novamente!")
                
                self.db.desconectar()
                
            except Exception as e:
                self.notify.error(f"Erro ao registar: {str(e)}")
                self.db.desconectar()
        
        # Botão Registar
        btn_registar = tk.Button(frame_botoes, text="✅ Registar",
                                command=fazer_registo,
                                font=FONTS['normal'],
                                bg=COLORS['success'],
                                fg='white',
                                relief='flat',
                                padx=30, pady=10,
                                cursor='hand2',
                                activebackground='#059669')
        btn_registar.pack(side='left', padx=10, fill='x', expand=True)
        
        # Botão Voltar
        btn_voltar = tk.Button(frame_botoes, text="⬅️ Voltar",
                              command=self.on_back_to_login,
                              font=FONTS['normal'],
                              bg=COLORS['disabled'],
                              fg=COLORS['text_primary'],
                              relief='flat',
                              padx=30, pady=10,
                              cursor='hand2',
                              activebackground='#cbd5e1')
        btn_voltar.pack(side='left', padx=10, fill='x', expand=True)
        
        # Permitir Enter para registo
        self.master.bind('<Return>', lambda e: fazer_registo())
        
        # Focar no campo de nome
        entry_nome.focus()
