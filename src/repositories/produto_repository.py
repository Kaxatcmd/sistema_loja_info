"""
Repositório de Produtos.

Encapsula todos os acessos à tabela ``produtos``.
A camada de UI e de serviços nunca deve escrever SQL de produtos
fora deste módulo.
"""

from src.database import DatabaseManager
from src.models.produto import Produto
from src.exceptions import DatabaseError

# Query base com LEFT JOIN para trazer nome_categoria
_SELECT_PRODUTOS = """
    SELECT p.*, c.nome AS nome_categoria
    FROM produtos p
    LEFT JOIN categorias c ON c.id_categoria = p.id_categoria
"""


class ProdutoRepository:
    """Repositório responsável pelas operações CRUD na tabela ``produtos``."""

    def __init__(self, db: DatabaseManager):
        self.db = db

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------

    def listar_todos(self) -> list[Produto]:
        """Devolve todos os produtos (com nome de categoria) ordenados por categoria e nome."""
        linhas = self.db.executar_query(
            _SELECT_PRODUTOS + " ORDER BY c.nome, p.nome"
        )
        return [Produto.from_dict(linha) for linha in (linhas or [])]

    def listar_por_categoria(self, id_categoria: int) -> list[Produto]:
        """Devolve apenas os produtos de uma categoria específica."""
        linhas = self.db.executar_query(
            _SELECT_PRODUTOS + " WHERE p.id_categoria = %s ORDER BY p.nome",
            (id_categoria,)
        )
        return [Produto.from_dict(linha) for linha in (linhas or [])]

    def buscar_por_id(self, id_produto: int) -> Produto | None:
        """Devolve o produto com o ID fornecido ou None se não existir."""
        linhas = self.db.executar_query(
            _SELECT_PRODUTOS + " WHERE p.id_produto = %s",
            (id_produto,)
        )
        return Produto.from_dict(linhas[0]) if linhas else None

    def buscar_por_nome(self, nome: str) -> list[Produto]:
        """Pesquisa produtos cujo nome contenha a expressão fornecida."""
        linhas = self.db.executar_query(
            _SELECT_PRODUTOS + " WHERE p.nome LIKE %s ORDER BY c.nome, p.nome",
            (f"%{nome}%",)
        )
        return [Produto.from_dict(linha) for linha in (linhas or [])]

    # ------------------------------------------------------------------
    # Escrita
    # ------------------------------------------------------------------

    def criar(self, produto: Produto) -> Produto:
        """Insere um novo produto na BD e devolve a instância com o ID gerado."""
        novo_id = self.db.executar_update(
            """
            INSERT INTO produtos (id_categoria, nome, descricao, preco, stock)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (produto.id_categoria, produto.nome, produto.descricao,
             produto.preco, produto.stock)
        )
        produto.id_produto = novo_id
        return produto

    def atualizar(self, produto: Produto) -> None:
        """Actualiza os dados de um produto existente."""
        if produto.id_produto is None:
            raise ValueError("id_produto não pode ser None para actualizar.")
        self.db.executar_update(
            """
            UPDATE produtos
               SET id_categoria = %s,
                   nome         = %s,
                   descricao    = %s,
                   preco        = %s,
                   stock        = %s
             WHERE id_produto = %s
            """,
            (produto.id_categoria, produto.nome, produto.descricao,
             produto.preco, produto.stock, produto.id_produto)
        )

    def deletar(self, id_produto: int) -> None:
        """Remove um produto da BD pelo seu ID."""
        self.db.executar_update(
            "DELETE FROM produtos WHERE id_produto = %s",
            (id_produto,)
        )

    def atualizar_stock(self, id_produto: int, quantidade: int) -> None:
        """Ajusta o stock de um produto (positivo para repor, negativo para vender)."""
        self.db.executar_update(
            "UPDATE produtos SET stock = stock + %s WHERE id_produto = %s",
            (quantidade, id_produto)
        )
