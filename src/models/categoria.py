"""
Modelo de Dados — Categoria de Produto
"""


class Categoria:
    """Modelo de Categoria de produtos informáticos."""

    def __init__(self, id_categoria=None, nome=None, descricao=None, data_criacao=None):
        self.id_categoria = id_categoria
        self.nome = nome
        self.descricao = descricao
        self.data_criacao = data_criacao

    @classmethod
    def from_dict(cls, data: dict) -> "Categoria":
        """Cria Categoria a partir de dicionário (resultado da BD)."""
        return cls(
            id_categoria=data.get('id_categoria'),
            nome=data.get('nome'),
            descricao=data.get('descricao'),
            data_criacao=data.get('data_criacao'),
        )

    def to_dict(self) -> dict:
        """Serializa a categoria para dicionário."""
        return {
            'id_categoria': self.id_categoria,
            'nome': self.nome,
            'descricao': self.descricao,
            'data_criacao': self.data_criacao,
        }

    def __repr__(self):
        return f"Categoria(id={self.id_categoria}, nome={self.nome!r})"
