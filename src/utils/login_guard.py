"""
Proteção contra Brute-Force no Login.

Rastreia tentativas de login falhadas por email.
Após atingir o limite definido em MAX_LOGIN_ATTEMPTS, o email
fica bloqueado durante LOGIN_LOCKOUT_SECONDS segundos.

O desbloqueio é automático — não requer intervenção manual.

Utilização::

    guard = LoginGuard()

    if guard.esta_bloqueado(email):
        segundos = guard.segundos_restantes(email)
        # mostrar mensagem ao utilizador

    # ... tentativa de login ...

    if login_falhou:
        guard.registar_falha(email)
    else:
        guard.resetar(email)
"""

import time
from src.config import MAX_LOGIN_ATTEMPTS, LOGIN_LOCKOUT_SECONDS
from src.utils.logger import obter_logger

logger = obter_logger(__name__)


class LoginGuard:
    """
    Controla tentativas de login falhadas e bloqueios temporários por email.

    Os dados são mantidos em memória — ao reiniciar a aplicação os
    contadores são resetados. Para persistência entre sessões seria
    necessário guardar na base de dados.
    """

    def __init__(self) -> None:
        # { email: {"falhas": int, "bloqueado_desde": float | None} }
        self._registos: dict[str, dict] = {}

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------

    def esta_bloqueado(self, email: str) -> bool:
        """
        Verifica se o email está atualmente bloqueado.

        O bloqueio expira automaticamente após LOGIN_LOCKOUT_SECONDS.

        Args:
            email: Email a verificar.

        Returns:
            True se bloqueado, False caso contrário.
        """
        registo = self._registos.get(email)
        if not registo:
            return False

        bloqueado_desde = registo.get("bloqueado_desde")
        if bloqueado_desde is None:
            return False

        # Verificar se o tempo de bloqueio já expirou
        if time.time() - bloqueado_desde >= LOGIN_LOCKOUT_SECONDS:
            self.resetar(email)
            logger.info("Bloqueio expirado para: %s", email)
            return False

        return True

    def segundos_restantes(self, email: str) -> int:
        """
        Calcula quantos segundos faltam para o desbloqueio.

        Args:
            email: Email bloqueado.

        Returns:
            Segundos restantes (0 se não estiver bloqueado).
        """
        registo = self._registos.get(email)
        if not registo or registo.get("bloqueado_desde") is None:
            return 0

        decorrido = time.time() - registo["bloqueado_desde"]
        restante = LOGIN_LOCKOUT_SECONDS - decorrido
        return max(0, int(restante))

    def tentativas_restantes(self, email: str) -> int:
        """
        Quantas tentativas restam antes do bloqueio.

        Args:
            email: Email a verificar.

        Returns:
            Número de tentativas restantes.
        """
        falhas = self._registos.get(email, {}).get("falhas", 0)
        return max(0, MAX_LOGIN_ATTEMPTS - falhas)

    # ------------------------------------------------------------------
    # Ações
    # ------------------------------------------------------------------

    def registar_falha(self, email: str) -> None:
        """
        Regista uma tentativa de login falhada.

        Se atingir MAX_LOGIN_ATTEMPTS, ativa o bloqueio automático.

        Args:
            email: Email que falhou o login.
        """
        if email not in self._registos:
            self._registos[email] = {"falhas": 0, "bloqueado_desde": None}

        self._registos[email]["falhas"] += 1
        falhas = self._registos[email]["falhas"]

        logger.warning(
            "Login falhado para '%s' — tentativa %d/%d",
            email, falhas, MAX_LOGIN_ATTEMPTS
        )

        if falhas >= MAX_LOGIN_ATTEMPTS:
            self._registos[email]["bloqueado_desde"] = time.time()
            logger.warning(
                "Email bloqueado por %ds após %d tentativas falhadas: %s",
                LOGIN_LOCKOUT_SECONDS, MAX_LOGIN_ATTEMPTS, email
            )

    def resetar(self, email: str) -> None:
        """
        Remove o registo de falhas de um email (login bem-sucedido ou expiração).

        Args:
            email: Email a resetar.
        """
        if email in self._registos:
            del self._registos[email]