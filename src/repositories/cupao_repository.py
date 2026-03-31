"""
Repositório de Cupões de Desconto.

Encapsula todos os acessos à tabela ``cupoes``; a UI e os serviços
usam este repositório em vez de chamar ``DatabaseManager`` directamente.
"""

from src.models.cupao import Cupao
from src.utils.logger import obter_logger

logger = obter_logger(__name__)


class CupaoRepository:
    """Repositório para operações CRUD sobre a tabela ``cupoes``."""

    def __init__(self, db) -> None:
        """
        Args:
            db: Instância de ``DatabaseManager`` (ou adaptador compatível).
        """
        self.db = db

    # ------------------------------------------------------------------
    # Leitura
    # ------------------------------------------------------------------

    def listar_todos(self) -> list[Cupao]:
        """Devolve todos os cupões ordenados por código."""
        linhas = self.db.executar_query(
            "SELECT * FROM cupoes ORDER BY codigo"
        )
        return [Cupao.from_dict(r) for r in linhas]

    def listar_ativos(self) -> list[Cupao]:
        """Devolve apenas os cupões activos."""
        linhas = self.db.executar_query(
            "SELECT * FROM cupoes WHERE ativo = %s ORDER BY codigo",
            (True,),
        )
        return [Cupao.from_dict(r) for r in linhas]

    def buscar_por_id(self, id_cupao: int) -> Cupao | None:
        """Devolve o cupão com o ID indicado ou ``None``."""
        linhas = self.db.executar_query(
            "SELECT * FROM cupoes WHERE id_cupao = %s", (id_cupao,)
        )
        return Cupao.from_dict(linhas[0]) if linhas else None

    def buscar_por_codigo(self, codigo: str) -> Cupao | None:
        """
        Devolve o cupão que corresponde ao código (case-insensitive) ou ``None``.

        O código é normalizado para maiúsculas antes da pesquisa.
        """
        linhas = self.db.executar_query(
            "SELECT * FROM cupoes WHERE UPPER(codigo) = UPPER(%s)", (codigo.strip(),)
        )
        return Cupao.from_dict(linhas[0]) if linhas else None

    # ------------------------------------------------------------------
    # Validação de uso
    # ------------------------------------------------------------------

    def validar_cupao(self, codigo: str) -> tuple[bool, Cupao | None, str]:
        """
        Verifica se o cupão existe, está activo e dentro da validade.

        Returns:
            Tuple ``(valido, cupao_ou_None, mensagem)``.
        """
        cupao = self.buscar_por_codigo(codigo)
        if cupao is None:
            return False, None, "Cupão não encontrado."
        if not cupao.esta_valido():
            return False, None, "Cupão inválido ou expirado."
        return True, cupao, "Cupão válido!"

    # ------------------------------------------------------------------
    # Escrita
    # ------------------------------------------------------------------

    def criar(self, cupao: Cupao) -> Cupao:
        """
        Insere um novo cupão na BD.

        Returns:
            A mesma instância com ``id_cupao`` preenchido.
        """
        data_validade = (
            cupao.data_validade.isoformat()
            if hasattr(cupao.data_validade, "isoformat")
            else cupao.data_validade
        )
        id_ = self.db.executar_update(
            "INSERT INTO cupoes (codigo, desconto, tipo, ativo, data_validade) "
            "VALUES (%s, %s, %s, %s, %s)",
            (
                cupao.codigo.strip().upper(),
                cupao.desconto,
                cupao.tipo,
                bool(cupao.ativo),
                data_validade,
            ),
        )
        cupao.id_cupao = id_
        logger.info("Cupão criado: %r (id=%s)", cupao.codigo, id_)
        return cupao

    def atualizar(self, cupao: Cupao) -> None:
        """
        Actualiza os dados de um cupão existente.

        Raises:
            ValueError: Se ``id_cupao`` for ``None``.
        """
        if cupao.id_cupao is None:
            raise ValueError("id_cupao é obrigatório para actualizar um cupão.")
        data_validade = (
            cupao.data_validade.isoformat()
            if hasattr(cupao.data_validade, "isoformat")
            else cupao.data_validade
        )
        self.db.executar_update(
            "UPDATE cupoes SET codigo=%s, desconto=%s, tipo=%s, "
            "ativo=%s, data_validade=%s WHERE id_cupao=%s",
            (
                cupao.codigo.strip().upper(),
                cupao.desconto,
                cupao.tipo,
                bool(cupao.ativo),
                data_validade,
                cupao.id_cupao,
            ),
        )
        logger.info("Cupão #%s actualizado.", cupao.id_cupao)

    def desativar(self, id_cupao: int) -> None:
        """Marca o cupão como inactivo sem o remover da BD."""
        self.db.executar_update(
            "UPDATE cupoes SET ativo=%s WHERE id_cupao=%s", (False, id_cupao)
        )
        logger.info("Cupão #%s desactivado.", id_cupao)

    def deletar(self, id_cupao: int) -> None:
        """Remove o cupão permanentemente da BD."""
        self.db.executar_update(
            "DELETE FROM cupoes WHERE id_cupao=%s", (id_cupao,)
        )
        logger.info("Cupão #%s eliminado.", id_cupao)
