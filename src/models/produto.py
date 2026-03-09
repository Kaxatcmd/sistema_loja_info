"""
Modelos de Dados - Produto
"""


class Produto:
    """Modelo de Produto"""
    
    def __init__(self, id_produto=None, nome=None, descricao=None, 
                 preco=None, stock=None, data_criacao=None):
        self.id_produto = id_produto
        self.nome = nome
        self.descricao = descricao
        self.preco = preco
        self.stock = stock
        self.data_criacao = data_criacao
    
    @classmethod
    def from_dict(cls, data):
        """Cria Produto a partir de dicionário (resultado da BD)"""
        return cls(
            id_produto=data.get('id_produto'),
            nome=data.get('nome'),
            descricao=data.get('descricao'),
            preco=data.get('preco'),
            stock=data.get('stock'),
            data_criacao=data.get('data_criacao')
        )
    
    def __repr__(self):
        return f"Produto(id={self.id_produto}, nome={self.nome}, preco={self.preco}, stock={self.stock})"
