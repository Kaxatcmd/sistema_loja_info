"""
Modelo de Dados — Avaliação de Produto

Cada cliente pode avaliar cada produto uma única vez.
A nota é um inteiro de 1 a 5 (validado na camada de repositório).
"""


class Avaliacao:
    """Modelo de Avaliação de Produto por um Cliente."""

    def __init__(
        self,
        id_avaliacao: int | None = None,
        id_cliente: int | None = None,
        id_produto: int | None = None,
        nota: int | None = None,
        comentario: str | None = None,
        data_criacao=None,
    ) -> None:
        self.id_avaliacao = id_avaliacao
        self.id_cliente = id_cliente
        self.id_produto = id_produto
        self.nota = nota                    # inteiro 1–5
        self.comentario = comentario
        self.data_criacao = data_criacao

    # ------------------------------------------------------------------
    # Construção a partir da BD
    # ------------------------------------------------------------------

    @classmethod
    def from_dict(cls, data: dict) -> "Avaliacao":
        """Cria Avaliacao a partir de dicionário (resultado da BD)."""
        return cls(
            id_avaliacao=data.get("id_avaliacao"),
            id_cliente=data.get("id_cliente"),
            id_produto=data.get("id_produto"),
            nota=data.get("nota"),
            comentario=data.get("comentario"),
            data_criacao=data.get("data_criacao"),
        )

    # ------------------------------------------------------------------
    # Serialização
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Serializa a avaliação para dicionário."""
        return {
            "id_avaliacao": self.id_avaliacao,
            "id_cliente": self.id_cliente,
            "id_produto": self.id_produto,
            "nota": self.nota,
            "comentario": self.comentario,
            "data_criacao": self.data_criacao,
        }

    def __repr__(self) -> str:
        return (
            f"Avaliacao(id={self.id_avaliacao}, id_cliente={self.id_cliente}, "
            f"id_produto={self.id_produto}, nota={self.nota})"
        )
