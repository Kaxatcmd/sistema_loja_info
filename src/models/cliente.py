"""
Modelos de Dados - Cliente
"""


class Cliente:
    """Modelo de Cliente"""
    
    def __init__(self, id_cliente=None, nome=None, email=None, 
                 telefone=None, password=None, is_admin=False, data_criacao=None):
        self.id_cliente = id_cliente
        self.nome = nome
        self.email = email
        self.telefone = telefone
        self.password = password
        self.is_admin = is_admin
        self.data_criacao = data_criacao
    
    @classmethod
    def from_dict(cls, data):
        """Cria Cliente a partir de dicionário (resultado da BD)"""
        return cls(
            id_cliente=data.get('id_cliente'),
            nome=data.get('nome'),
            email=data.get('email'),
            telefone=data.get('telefone'),
            password=data.get('password'),
            is_admin=data.get('is_admin', False),
            data_criacao=data.get('data_criacao')
        )
    
    def __repr__(self):
        return f"Cliente(id={self.id_cliente}, nome={self.nome}, email={self.email}, is_admin={self.is_admin})"
