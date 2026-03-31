"""
Modelo de Dados — Wishlist (Lista de Desejos)

Regista os produtos que um cliente marcou como desejados.
A combinação (id_cliente, id_produto) é única — um produto
só pode aparecer uma vez na lista de cada cliente.
"""


class Wishlist:
    """Modelo de item da Wishlist (produto desejado por um cliente)."""

    def __init__(
        self,
        id_wishlist: int | None = None,
        id_cliente: int | None = None,
        id_produto: int | None = None,
        data_criacao=None,
    ) -> None:
        self.id_wishlist = id_wishlist
        self.id_cliente = id_cliente
        self.id_produto = id_produto
        self.data_criacao = data_criacao

    # ------------------------------------------------------------------
    # Construção a partir da BD
    # ------------------------------------------------------------------

    @classmethod
    def from_dict(cls, data: dict) -> "Wishlist":
        """Cria Wishlist a partir de dicionário (resultado da BD)."""
        return cls(
            id_wishlist=data.get("id_wishlist"),
            id_cliente=data.get("id_cliente"),
            id_produto=data.get("id_produto"),
            data_criacao=data.get("data_criacao"),
        )

    # ------------------------------------------------------------------
    # Serialização
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Serializa o item de wishlist para dicionário."""
        return {
            "id_wishlist": self.id_wishlist,
            "id_cliente": self.id_cliente,
            "id_produto": self.id_produto,
            "data_criacao": self.data_criacao,
        }

    def __repr__(self) -> str:
        return (
            f"Wishlist(id={self.id_wishlist}, id_cliente={self.id_cliente}, "
            f"id_produto={self.id_produto})"
        )
