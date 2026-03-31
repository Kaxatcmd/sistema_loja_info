"""
Repositório de Produtos.

Encapsula todos os acessos à tabela ``produtos``.
A camada de UI e de serviços nunca deve escrever SQL de produtos
fora deste módulo.
"""

from src.database import DatabaseManager
from src.models.produto import Produto
from src.exceptions import DatabaseError


class ProdutoRepository:
    """Repositório responsável pelas operações CRUD na tabela ``produtos``."""

    def __init__(self, db: DatabaseManager):
        """
        Inicializa o repositório com uma instância de DatabaseManager.

        Args:
            db (DatabaseManager): Instância já conectada ao servidor de BD.
        """
        self.db = db

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------

    def listar_todos(self) -> list[Produto]:
        """
        Devolve todos os produtos ordenados por nome.

        Returns:
            list[Produto]: Lista de produtos (pode ser vazia).

        Raises:
            DatabaseError: Se ocorrer um erro de BD.
        """
        linhas = self.db.executar_query(
            "SELECT * FROM produtos ORDER BY nome"
        )
        return [Produto.from_dict(linha) for linha in (linhas or [])]

    def buscar_por_id(self, id_produto: int) -> Produto | None:
        """
        Devolve o produto com o ID fornecido ou ``None`` se não existir.

        Args:
            id_produto (int): Identificador único do produto.

        Returns:
            Produto | None: Produto encontrado ou None.

        Raises:
            DatabaseError: Se ocorrer um erro de BD.
        """
        linhas = self.db.executar_query(
            "SELECT * FROM produtos WHERE id_produto = %s",
            (id_produto,)
        )
        if not linhas:
            return None
        return Produto.from_dict(linhas[0])

    def buscar_por_nome(self, nome: str) -> list[Produto]:
        """
        Pesquisa produtos cujo nome contenha a expressão fornecida
        (pesquisa parcial, sem distinção de maiúsculas/minúsculas).

        Args:
            nome (str): Texto a pesquisar no nome do produto.

        Returns:
            list[Produto]: Lista de produtos correspondentes.

        Raises:
            DatabaseError: Se ocorrer um erro de BD.
        """
        linhas = self.db.executar_query(
            "SELECT * FROM produtos WHERE nome LIKE %s ORDER BY nome",
            (f"%{nome}%",)
        )
        return [Produto.from_dict(linha) for linha in (linhas or [])]

    # ------------------------------------------------------------------
    # Escrita
    # ------------------------------------------------------------------

    def criar(self, produto: Produto) -> Produto:
        """
        Insere um novo produto na BD e devolve a instância com o ID gerado.

        Args:
            produto (Produto): Produto a inserir (``id_produto`` deve ser None).

        Returns:
            Produto: O mesmo objecto com ``id_produto`` preenchido.

        Raises:
            DatabaseError: Se ocorrer um erro de BD.
        """
        novo_id = self.db.executar_update(
            """
            INSERT INTO produtos (nome, descricao, preco, stock)
            VALUES (%s, %s, %s, %s)
            """,
            (produto.nome, produto.descricao, produto.preco, produto.stock)
        )
        produto.id_produto = novo_id
        return produto

    def atualizar(self, produto: Produto) -> None:
        """
        Actualiza os dados de um produto existente.

        Args:
            produto (Produto): Produto com os novos valores.
                               O campo ``id_produto`` deve estar preenchido.

        Raises:
            DatabaseError: Se ocorrer um erro de BD.
            ValueError: Se ``id_produto`` for None.
        """
        if produto.id_produto is None:
            raise ValueError("id_produto não pode ser None para actualizar.")

        self.db.executar_update(
            """
            UPDATE produtos
               SET nome      = %s,
                   descricao = %s,
                   preco     = %s,
                   stock     = %s
             WHERE id_produto = %s
            """,
            (produto.nome, produto.descricao, produto.preco,
             produto.stock, produto.id_produto)
        )

    def deletar(self, id_produto: int) -> None:
        """
        Remove um produto da BD pelo seu ID.

        Args:
            id_produto (int): Identificador do produto a remover.

        Raises:
            DatabaseError: Se ocorrer um erro de BD.
        """
        self.db.executar_update(
            "DELETE FROM produtos WHERE id_produto = %s",
            (id_produto,)
        )

    def atualizar_stock(self, id_produto: int, quantidade: int) -> None:
        """
        Ajusta o stock de um produto (pode ser positivo ou negativo).

        Use valores negativos para decrementar (ex.: venda) e positivos
        para incrementar (ex.: reposição de stock).

        Args:
            id_produto (int): Identificador do produto.
            quantidade (int): Variação de stock a aplicar.

        Raises:
            DatabaseError: Se ocorrer um erro de BD.
        """
        self.db.executar_update(
            "UPDATE produtos SET stock = stock + %s WHERE id_produto = %s",
            (quantidade, id_produto)
        )
