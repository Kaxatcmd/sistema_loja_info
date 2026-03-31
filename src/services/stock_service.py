"""
Serviço de Notificações de Stock Baixo.

Responsabilidades:
  - Detectar produtos com stock abaixo do limiar configurável.
  - Gerar mensagens de alerta formatadas.
  - Registar alertas no log da aplicação.

Este módulo não tem dependência de Tkinter e pode ser testado de forma
isolada sem necessitar de um servidor de BD (desde que seja fornecido
um adaptador compatível com DatabaseManager).
"""

from src.config import STOCK_MINIMO
from src.models.produto import Produto
from src.utils.logger import obter_logger

logger = obter_logger(__name__)


class StockService:
    """
    Serviço de monitorização de stock.

    Recebe um ``DatabaseManager`` (ou adaptador compatível) no construtor
    e oferece métodos para consultar produtos com stock baixo e gerar
    alertas.

    Exemplo de uso::

        servico = StockService(db)
        alertas = servico.obter_alertas()
        for alerta in alertas:
            print(alerta)
    """

    def __init__(self, db, limiar: int = STOCK_MINIMO) -> None:
        """
        Args:
            db:      Instância de ``DatabaseManager`` ou adaptador compatível.
            limiar:  Stock mínimo aceitável (incluído).  Produtos com stock
                     estritamente inferior a este valor são considerados em
                     alerta.  Por omissão usa ``STOCK_MINIMO`` de ``config.py``.
        """
        if limiar < 0:
            raise ValueError("O limiar de stock não pode ser negativo.")
        self.db = db
        self.limiar = limiar

    # ------------------------------------------------------------------
    # Interface pública
    # ------------------------------------------------------------------

    def produtos_stock_baixo(self) -> list[Produto]:
        """
        Devolve a lista de produtos cujo stock está abaixo do limiar.

        Os produtos são ordenados por stock crescente (os mais críticos
        primeiro) e depois por nome.

        Returns:
            Lista de instâncias :class:`~src.models.produto.Produto`.
        """
        linhas = self.db.executar_query(
            "SELECT * FROM produtos WHERE stock < %s ORDER BY stock ASC, nome ASC",
            (self.limiar,),
        )
        produtos = [Produto.from_dict(r) for r in linhas]
        if produtos:
            logger.warning(
                "Stock baixo detectado: %d produto(s) com stock < %d.",
                len(produtos),
                self.limiar,
            )
        return produtos

    def obter_alertas(self) -> list[str]:
        """
        Devolve uma lista de strings com as mensagens de alerta prontas a
        ser exibidas na UI ou escritas no log.

        Returns:
            Lista de strings no formato
            ``"⚠ <nome> — stock: <n> (mínimo: <limiar>)"``.
            Lista vazia se não houver produtos em alerta.
        """
        return [
            f"⚠ {p.nome} — stock: {p.stock} (mínimo: {self.limiar})"
            for p in self.produtos_stock_baixo()
        ]

    def tem_alertas(self) -> bool:
        """Devolve ``True`` se existir pelo menos um produto em stock baixo."""
        linhas = self.db.executar_query(
            "SELECT COUNT(*) AS total FROM produtos WHERE stock < %s",
            (self.limiar,),
        )
        return int(linhas[0]["total"]) > 0 if linhas else False

    def resumo(self) -> str:
        """
        Devolve uma string resumida para usar em banners de alerta.

        Returns:
            Exemplo: ``"3 produto(s) com stock abaixo de 5 unidades."``
            Se não houver alertas devolve string vazia.
        """
        produtos = self.produtos_stock_baixo()
        if not produtos:
            return ""
        return (
            f"{len(produtos)} produto(s) com stock abaixo de "
            f"{self.limiar} unidade(s)."
        )
