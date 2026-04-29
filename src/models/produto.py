"""
Modelos de Dados - Produto
"""


class Produto:
    """Modelo de Produto"""
    
    def __init__(self, id_produto=None, id_categoria=None, nome=None, descricao=None,
                 preco=None, stock=None, data_criacao=None, nome_categoria=None):
        self.id_produto = id_produto
        self.id_categoria = id_categoria
        self.nome = nome
        self.descricao = descricao
        self.preco = preco
        self.stock = stock
        self.data_criacao = data_criacao
        # Campo calculado via JOIN (não existe na tabela produtos)
        self.nome_categoria = nome_categoria

    @classmethod
    def from_dict(cls, data):
        """Cria Produto a partir de dicionário (resultado da BD)"""
        raw_preco = data.get('preco')
        return cls(
            id_produto=data.get('id_produto'),
            id_categoria=data.get('id_categoria'),
            nome=data.get('nome'),
            descricao=data.get('descricao'),
            preco=float(raw_preco) if raw_preco is not None else None,
            stock=data.get('stock'),
            data_criacao=data.get('data_criacao'),
            nome_categoria=data.get('nome_categoria'),
        )

    def to_dict(self) -> dict:
        """Serializa o produto para dicionário."""
        return {
            "id_produto": self.id_produto,
            "id_categoria": self.id_categoria,
            "nome": self.nome,
            "descricao": self.descricao,
            "preco": self.preco,
            "stock": self.stock,
            "data_criacao": self.data_criacao,
            "nome_categoria": self.nome_categoria,
        }

    def __repr__(self):
        return (f"Produto(id={self.id_produto}, nome={self.nome}, "
                f"categoria={self.nome_categoria!r}, preco={self.preco}, stock={self.stock})")
