"""
Repositório de Categorias.

Encapsula todos os acessos à tabela ``categorias``.
"""

from src.database import DatabaseManager
from src.models.categoria import Categoria
from src.exceptions import DatabaseError


class CategoriaRepository:
    """Repositório responsável pelas operações CRUD na tabela ``categorias``."""

    def __init__(self, db: DatabaseManager):
        self.db = db

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------

    def listar_todos(self) -> list[Categoria]:
        """Devolve todas as categorias ordenadas por nome."""
        linhas = self.db.executar_query(
            "SELECT * FROM categorias ORDER BY nome"
        )
        return [Categoria.from_dict(linha) for linha in (linhas or [])]

    def buscar_por_id(self, id_categoria: int) -> Categoria | None:
        """Devolve a categoria com o ID fornecido ou None se não existir."""
        linhas = self.db.executar_query(
            "SELECT * FROM categorias WHERE id_categoria = %s",
            (id_categoria,)
        )
        return Categoria.from_dict(linhas[0]) if linhas else None

    # ------------------------------------------------------------------
    # Escrita
    # ------------------------------------------------------------------

    def criar(self, categoria: Categoria) -> Categoria:
        """Insere uma nova categoria e devolve a instância com o ID gerado."""
        novo_id = self.db.executar_update(
            "INSERT INTO categorias (nome, descricao) VALUES (%s, %s)",
            (categoria.nome, categoria.descricao)
        )
        categoria.id_categoria = novo_id
        return categoria

    def atualizar(self, categoria: Categoria) -> None:
        """Actualiza nome e descrição de uma categoria existente."""
        if categoria.id_categoria is None:
            raise ValueError("id_categoria não pode ser None para actualizar.")
        self.db.executar_update(
            "UPDATE categorias SET nome = %s, descricao = %s WHERE id_categoria = %s",
            (categoria.nome, categoria.descricao, categoria.id_categoria)
        )

    def deletar(self, id_categoria: int) -> None:
        """
        Remove a categoria.
        Os produtos associados ficam com id_categoria = NULL
        (ON DELETE SET NULL definido na FK de produtos).
        """
        self.db.executar_update(
            "DELETE FROM categorias WHERE id_categoria = %s",
            (id_categoria,)
        )

    def contar_produtos(self, id_categoria: int) -> int:
        """Devolve o número de produtos associados a esta categoria."""
        linhas = self.db.executar_query(
            "SELECT COUNT(*) AS total FROM produtos WHERE id_categoria = %s",
            (id_categoria,)
        )
        return linhas[0]['total'] if linhas else 0
