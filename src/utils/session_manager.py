"""
Gestão de Sessão com Expiração por Inatividade.

Monitoriza o último momento de interação do utilizador.
Se não houver interação durante SESSION_TIMEOUT_SECONDS segundos,
a sessão expira e o callback de logout é invocado automaticamente.

O temporizador é gerido pelo próprio Tkinter (método ``after``),
pelo que não são necessárias threads adicionais.

Utilização::

    def fazer_logout():
        # lógica de logout da aplicação
        ...

    session = SessionManager(root, on_expire=fazer_logout)
    session.iniciar()

    # Registar interações do utilizador:
    root.bind_all("<Motion>",   session.registar_atividade)
    root.bind_all("<Key>",      session.registar_atividade)
    root.bind_all("<Button>",   session.registar_atividade)

    # Ao fazer logout manual:
    session.parar()
"""

import time
from src.config import SESSION_TIMEOUT_SECONDS
from src.utils.logger import obter_logger

logger = obter_logger(__name__)


class SessionManager:
    """
    Controla a expiração de sessão por inatividade.

    Usa o método ``after`` do Tkinter para verificar periodicamente
    se o timeout foi atingido, sem bloquear a interface gráfica.
    """

    # Intervalo de verificação (em milissegundos)
    _INTERVALO_VERIFICACAO_MS = 10_000  # verifica a cada 10 segundos

    def __init__(self, root, on_expire: callable) -> None:
        """
        Args:
            root:      Janela raiz do Tkinter.
            on_expire: Função chamada quando a sessão expira.
                       Deve realizar o logout e redirecionar para o login.
        """
        self._root = root
        self._on_expire = on_expire
        self._ultimo_ativo: float = time.time()
        self._ativo: bool = False
        self._job = None  # referência ao ``after`` agendado

    # ------------------------------------------------------------------
    # Ciclo de vida
    # ------------------------------------------------------------------

    def iniciar(self) -> None:
        """
        Inicia o temporizador de sessão.

        Deve ser chamado imediatamente após o login bem-sucedido.
        """
        self._ultimo_ativo = time.time()
        self._ativo = True
        self._agendar_verificacao()
        logger.info(
            "Sessão iniciada — timeout configurado para %ds.",
            SESSION_TIMEOUT_SECONDS
        )

    def parar(self) -> None:
        """
        Para o temporizador de sessão.

        Deve ser chamado no logout manual para evitar callbacks indesejados.
        """
        self._ativo = False
        if self._job is not None:
            try:
                self._root.after_cancel(self._job)
            except Exception:
                pass
            self._job = None
        logger.info("Sessão terminada manualmente.")

    # ------------------------------------------------------------------
    # Atividade
    # ------------------------------------------------------------------

    def registar_atividade(self, event=None) -> None:
        """
        Atualiza o timestamp da última interação.

        Deve ser ligado aos eventos de input do Tkinter::

            root.bind_all("<Motion>", session.registar_atividade)
            root.bind_all("<Key>",    session.registar_atividade)
            root.bind_all("<Button>", session.registar_atividade)

        Args:
            event: Evento Tkinter (ignorado, apenas para compatibilidade).
        """
        self._ultimo_ativo = time.time()

    def tempo_inativo(self) -> int:
        """
        Segundos desde a última interação do utilizador.

        Returns:
            Segundos de inatividade.
        """
        return int(time.time() - self._ultimo_ativo)

    # ------------------------------------------------------------------
    # Verificação interna
    # ------------------------------------------------------------------

    def _agendar_verificacao(self) -> None:
        """Agenda a próxima verificação de timeout."""
        if self._ativo:
            self._job = self._root.after(
                self._INTERVALO_VERIFICACAO_MS,
                self._verificar_timeout
            )

    def _verificar_timeout(self) -> None:
        """
        Verifica se o tempo de inatividade foi excedido.

        Se sim, invoca o callback de expiração.
        Se não, agenda a próxima verificação.
        """
        if not self._ativo:
            return

        inativo = self.tempo_inativo()

        if inativo >= SESSION_TIMEOUT_SECONDS:
            logger.warning(
                "Sessão expirada por inatividade (%ds sem interação).", inativo
            )
            self._ativo = False
            self._on_expire()
        else:
            self._agendar_verificacao()