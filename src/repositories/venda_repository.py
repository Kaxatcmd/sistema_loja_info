"""
Repositório de Vendas.

Encapsula todos os acessos às tabelas ``vendas`` e ``venda_produto``.
Uma venda é sempre criada de forma atómica: o registo em ``vendas`` e
todos os itens em ``venda_produto`` são inseridos na mesma operação
(a atomicidade é garantida pela transacção do DatabaseManager).
"""

from datetime import date
from src.database import DatabaseManager
from src.exceptions import DatabaseError


class VendaRepository:
    """
    Repositório responsável pelas operações sobre vendas.

    Trabalha com as tabelas ``vendas`` e ``venda_produto``.
    Os itens de uma venda são listas de dicionários com as chaves
    ``id_produto``, ``preco`` e ``quantidade``.
    """

    def __init__(self, db: DatabaseManager):
        """
        Inicializa o repositório com uma instância de DatabaseManager.

        Args:
            db (DatabaseManager): Instância já conectada ao servidor de BD.
        """
        self.db = db

    # ------------------------------------------------------------------
    # Escrita
    # ------------------------------------------------------------------

    def criar_venda(self, cliente_id: int, itens: list[dict]) -> int:
        """
        Cria uma venda completa (cabeçalho + itens) e actualiza o stock.

        Os itens são processados sequencialmente. Se qualquer operação de
        BD falhar, DatabaseError é lançada (a rollback é feita pelo
        DatabaseManager).

        Estrutura esperada de cada item::

            {
                "id_produto": int,
                "preco":      float,
                "quantidade": int,
            }

        Args:
            cliente_id (int): ID do cliente que efectua a compra.
            itens (list[dict]): Lista de itens da venda.

        Returns:
            int: ID da venda criada.

        Raises:
            DatabaseError: Se ocorrer qualquer erro de BD durante a criação.
            ValueError: Se ``itens`` estiver vazio.
        """
        if not itens:
            raise ValueError("Não é possível criar uma venda sem itens.")

        # Calcular total a partir dos itens
        total = sum(
            item["preco"] * item["quantidade"]
            for item in itens
        )

        # Inserir cabeçalho da venda
        id_venda = self.db.executar_update(
            """
            INSERT INTO vendas (id_cliente, data, total)
            VALUES (%s, %s, %s)
            """,
            (cliente_id, date.today(), total)
        )

        # Inserir itens e actualizar stock
        for item in itens:
            self.db.executar_update(
                """
                INSERT INTO venda_produto (id_venda, id_produto, preco, quantidade)
                VALUES (%s, %s, %s, %s)
                """,
                (id_venda, item["id_produto"], item["preco"], item["quantidade"])
            )
            self.db.executar_update(
                "UPDATE produtos SET stock = stock - %s WHERE id_produto = %s",
                (item["quantidade"], item["id_produto"])
            )

        return id_venda

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------

    def historico_cliente(self, cliente_id: int) -> list[dict]:
        """
        Devolve o histórico de vendas de um cliente específico.

        Cada entrada inclui os dados da venda e os respectivos itens
        (produtos comprados).

        Args:
            cliente_id (int): ID do cliente.

        Returns:
            list[dict]: Lista de vendas com os campos:
                ``id_venda``, ``data``, ``total``,
                ``id_produto``, ``nome_produto``, ``preco_unitario``, ``quantidade``.

        Raises:
            DatabaseError: Se ocorrer um erro de BD.
        """
        linhas = self.db.executar_query(
            """
            SELECT v.id_venda,
                   v.data,
                   v.total,
                   p.id_produto,
                   p.nome        AS nome_produto,
                   vp.preco      AS preco_unitario,
                   vp.quantidade
              FROM vendas v
              JOIN venda_produto vp ON vp.id_venda    = v.id_venda
              JOIN produtos      p  ON p.id_produto   = vp.id_produto
             WHERE v.id_cliente = %s
             ORDER BY v.data DESC, v.id_venda DESC
            """,
            (cliente_id,)
        )
        return linhas or []

    def historico_geral(self, limite: int = 100) -> list[dict]:
        """
        Devolve o histórico geral de vendas (para o painel de administrador).

        Args:
            limite (int): Número máximo de vendas a devolver (default: 100).

        Returns:
            list[dict]: Lista de vendas com os campos:
                ``id_venda``, ``nome_cliente``, ``data``, ``total``.

        Raises:
            DatabaseError: Se ocorrer um erro de BD.
        """
        linhas = self.db.executar_query(
            """
            SELECT v.id_venda,
                   c.nome  AS nome_cliente,
                   v.data,
                   v.total
              FROM vendas   v
              JOIN clientes c ON c.id_cliente = v.id_cliente
             ORDER BY v.data DESC, v.id_venda DESC
             LIMIT %s
            """,
            (limite,)
        )
        return linhas or []

    def total_vendas_periodo(self, data_inicio: date, data_fim: date) -> float:
        """
        Calcula o total de vendas num intervalo de datas (inclusive).

        Args:
            data_inicio (date): Data de início do período.
            data_fim (date): Data de fim do período.

        Returns:
            float: Soma dos totais das vendas no período, ou 0.0 se não houver.

        Raises:
            DatabaseError: Se ocorrer um erro de BD.
        """
        linhas = self.db.executar_query(
            """
            SELECT COALESCE(SUM(total), 0) AS soma_total
              FROM vendas
             WHERE data BETWEEN %s AND %s
            """,
            (data_inicio, data_fim)
        )
        if linhas:
            return float(linhas[0]["soma_total"])
        return 0.0
