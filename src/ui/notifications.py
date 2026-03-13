"""
Sistema de Notificações Interno
Exibe avisos e mensagens dentro da app, sem popups externos
"""

import tkinter as tk
from src.config import COLORS, FONTS


class NotificationManager:
    """Gerencia notificações dentro da aplicação"""
    
    def __init__(self, master):
        """
        Inicializa o gerenciador de notificações
        
        Args:
            master: Janela raiz Tkinter
        """
        self.master = master
        self.notification_frame = None
        self.notification_container = None
        self.hide_timer = None
        self.animation_id = None
        
        # Criar frame permanente para notificações (nunca será destruído)
        self._criar_frame_permanente()
        
        # Cores para diferentes tipos de notificação
        self.colors = {
            'info': {
                'bg': COLORS['info'],
                'fg': 'white',
                'icon': 'ℹ️'
            },
            'success': {
                'bg': COLORS['success'],
                'fg': 'white',
                'icon': '✅'
            },
            'warning': {
                'bg': COLORS['warning'],
                'fg': 'white',
                'icon': '⚠️'
            },
            'error': {
                'bg': COLORS['danger'],
                'fg': 'white',
                'icon': '❌'
            }
        }
    
    def _criar_frame_permanente(self):
        """Cria um frame permanente no topo que nunca é destruído"""
        self.notification_frame = tk.Frame(self.master, bg=COLORS['bg'], height=0)
        # Usar place() com lift() para ficar acima sem afetar layout
        self.notification_frame.place(x=0, y=0, relwidth=1.0, height=0)
        self.notification_frame.lift()  # Coloca acima de todos os outros widgets
    
    def _mostrar_notificacao(self, mensagem, tipo='info', duracao=4):
        """
        Mostra notificação na parte superior da app
        
        Args:
            mensagem: Texto a exibir
            tipo: 'info', 'success', 'warning', 'error'
            duracao: Tempo em segundos antes de desaparecer (0 = não desaparece)
        """
        # Cancelar timer anterior se existir
        if self.hide_timer is not None:
            self.master.after_cancel(self.hide_timer)
            self.hide_timer = None
        
        # Limpar notificação anterior
        if self.notification_container is not None:
            self.notification_container.destroy()
            self.notification_container = None
        
        # Obter cores
        cores = self.colors.get(tipo, self.colors['info'])
        
        # Container
        self.notification_container = tk.Frame(self.notification_frame, bg=cores['bg'])
        self.notification_container.pack(fill='x', padx=0, pady=0)
        
        # Conteúdo
        content = tk.Frame(self.notification_container, bg=cores['bg'])
        content.pack(fill='both', expand=True, padx=15, pady=10)
        
        # Ícone + Mensagem
        msg_frame = tk.Frame(content, bg=cores['bg'])
        msg_frame.pack(fill='x')
        
        # Ícone
        lbl_icon = tk.Label(msg_frame, text=cores['icon'], font=("Arial", 16),
                           fg=cores['fg'], bg=cores['bg'])
        lbl_icon.pack(side='left', padx=(0, 10))
        
        # Mensagem
        lbl_msg = tk.Label(msg_frame, text=mensagem,
                          font=FONTS['normal'],
                          fg=cores['fg'],
                          bg=cores['bg'],
                          wraplength=600,
                          justify='left')
        lbl_msg.pack(side='left', fill='x', expand=True)
        
        # Botão fechar (X)
        btn_close = tk.Label(msg_frame, text="✕", font=("Arial", 14),
                            fg=cores['fg'], bg=cores['bg'],
                            cursor='hand2')
        btn_close.pack(side='right', padx=(10, 0))
        btn_close.bind('<Button-1>', lambda e: self._ocultar_notificacao())
        
        # Atualizar altura do frame com place() em vez de config()
        num_linhas = mensagem.count('\n') + 1
        altura = max(60, 20 + num_linhas * 30)
        self.notification_frame.place(x=0, y=0, relwidth=1.0, height=altura)
        self.notification_frame.lift()  # Garantir que fica acima
        
        # Auto-hide se duracao > 0
        if duracao > 0:
            self.hide_timer = self.master.after(duracao * 1000, self._ocultar_notificacao)
    
    def _ocultar_notificacao(self):
        """Oculta a notificação"""
        if self.hide_timer is not None:
            self.master.after_cancel(self.hide_timer)
            self.hide_timer = None
        
        if self.animation_id is not None:
            self.master.after_cancel(self.animation_id)
            self.animation_id = None
        
        if self.notification_container is not None:
            self.notification_container.destroy()
            self.notification_container = None
        
        # Resetar altura com place() em vez de config()
        self.notification_frame.place(x=0, y=0, relwidth=1.0, height=0)
    
    def info(self, mensagem, duracao=3):
        """Mostra notificação de informação"""
        self._mostrar_notificacao(mensagem, 'info', duracao)
    
    def success(self, mensagem, duracao=3):
        """Mostra notificação de sucesso"""
        self._mostrar_notificacao(mensagem, 'success', duracao)
    
    def warning(self, mensagem, duracao=4):
        """Mostra notificação de aviso"""
        self._mostrar_notificacao(mensagem, 'warning', duracao)
    
    def error(self, mensagem, duracao=5):
        """Mostra notificação de erro"""
        self._mostrar_notificacao(mensagem, 'error', duracao)
    
    def question(self, mensagem, titulo="Confirmar", callback=None):
        """
        Mostra diálogo de confirmação dentro da app
        
        Args:
            mensagem: Texto a exibir
            titulo: Título do diálogo
            callback: Função a chamar com True/False
        """
        # Criar janela de diálogo
        dialog = tk.Toplevel(self.master)
        dialog.title(titulo)
        dialog.geometry("400x200")
        dialog.configure(bg=COLORS['bg'])
        dialog.resizable(False, False)
        
        # Centralizar na janela principal
        dialog.transient(self.master)
        dialog.grab_set()
        
        # Container principal
        frame_main = tk.Frame(dialog, bg=COLORS['bg'])
        frame_main.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Ícone + Mensagem
        frame_msg = tk.Frame(frame_main, bg=COLORS['bg'])
        frame_msg.pack(fill='x', pady=(0, 20))
        
        lbl_icon = tk.Label(frame_msg, text="❓", font=("Arial", 28),
                           bg=COLORS['bg'])
        lbl_icon.pack(side='left', padx=(0, 15))
        
        lbl_msg = tk.Label(frame_msg, text=mensagem, font=FONTS['normal'],
                          fg=COLORS['text_primary'], bg=COLORS['bg'],
                          wraplength=300, justify='left')
        lbl_msg.pack(side='left', fill='x', expand=True)
        
        # Botões
        frame_botoes = tk.Frame(frame_main, bg=COLORS['bg'])
        frame_botoes.pack(fill='x', pady=(20, 0))
        
        resultado = {'resposta': None}
        
        def sim():
            resultado['resposta'] = True
            if callback:
                callback(True)
            dialog.destroy()
        
        def nao():
            resultado['resposta'] = False
            if callback:
                callback(False)
            dialog.destroy()
        
        btn_sim = tk.Button(frame_botoes, text="✅ Sim",
                           command=sim,
                           font=FONTS['normal'],
                           bg=COLORS['success'],
                           fg='white',
                           relief='flat',
                           padx=25, pady=8,
                           cursor='hand2',
                           activebackground='#059669')
        btn_sim.pack(side='left', padx=5, fill='x', expand=True)
        
        btn_nao = tk.Button(frame_botoes, text="❌ Não",
                           command=nao,
                           font=FONTS['normal'],
                           bg=COLORS['danger'],
                           fg='white',
                           relief='flat',
                           padx=25, pady=8,
                           cursor='hand2',
                           activebackground='#dc2626')
        btn_nao.pack(side='left', padx=5, fill='x', expand=True)
        
        # Focar no botão Sim
        btn_sim.focus()
        
        # Permitir Enter para confirmar
        dialog.bind('<Return>', lambda e: sim())
        dialog.bind('<Escape>', lambda e: nao())
        
        return resultado['resposta']
