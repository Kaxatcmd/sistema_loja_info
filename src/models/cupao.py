"""
Modelo de Dados — Cupão de Desconto

Um cupão pode ser de dois tipos:
  - ``percentagem`` — desconto percentual sobre o total da venda
  - ``fixo``        — valor absoluto deduzido do total da venda
"""

from datetime import date


class Cupao:
    """Modelo de Cupão de Desconto."""

    def __init__(
        self,
        id_cupao: int | None = None,
        codigo: str | None = None,
        desconto: float | None = None,
        tipo: str = "percentagem",
        ativo: bool = True,
        data_validade: date | None = None,
        data_criacao=None,
    ) -> None:
        self.id_cupao = id_cupao
        self.codigo = codigo
        self.desconto = desconto
        self.tipo = tipo                    # 'percentagem' | 'fixo'
        self.ativo = ativo
        self.data_validade = data_validade
        self.data_criacao = data_criacao

    # ------------------------------------------------------------------
    # Construção a partir da BD
    # ------------------------------------------------------------------

    @classmethod
    def from_dict(cls, data: dict) -> "Cupao":
        """Cria Cupao a partir de dicionário (resultado da BD)."""
        raw_desconto = data.get("desconto")
        return cls(
            id_cupao=data.get("id_cupao"),
            codigo=data.get("codigo"),
            desconto=float(raw_desconto) if raw_desconto is not None else None,
            tipo=data.get("tipo", "percentagem"),
            ativo=bool(data.get("ativo", True)),
            data_validade=data.get("data_validade"),
            data_criacao=data.get("data_criacao"),
        )

    # ------------------------------------------------------------------
    # Serialização
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Serializa o cupão para dicionário."""
        return {
            "id_cupao": self.id_cupao,
            "codigo": self.codigo,
            "desconto": self.desconto,
            "tipo": self.tipo,
            "ativo": self.ativo,
            "data_validade": (
                self.data_validade.isoformat()
                if hasattr(self.data_validade, "isoformat")
                else self.data_validade
            ),
            "data_criacao": self.data_criacao,
        }

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------

    def esta_valido(self) -> bool:
        """Devolve True se o cupão está activo e dentro da validade."""
        if not self.ativo:
            return False
        if self.data_validade is None:
            return True
        hoje = date.today()
        validade = (
            self.data_validade
            if isinstance(self.data_validade, date)
            else date.fromisoformat(str(self.data_validade))
        )
        return validade >= hoje

    def calcular_desconto(self, total: float) -> float:
        """Devolve o valor do desconto a aplicar sobre *total*."""
        if self.desconto is None:
            return 0.0
        if self.tipo == "percentagem":
            return round(total * self.desconto / 100, 2)
        return min(round(float(self.desconto), 2), total)

    def __repr__(self) -> str:
        return (
            f"Cupao(id={self.id_cupao}, codigo={self.codigo!r}, "
            f"desconto={self.desconto}, tipo={self.tipo!r}, ativo={self.ativo})"
        )
