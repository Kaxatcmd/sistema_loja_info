"""
Pacote de Repositórios.

Cada repositório encapsula todos os acessos à BD para uma entidade
específica, seguindo o padrão Repository. A UI e os serviços utilizam
os repositórios em vez de chamar DatabaseManager directamente.

Repositórios disponíveis:
    - ProdutoRepository  — operações sobre a tabela ``produtos``
    - ClienteRepository  — operações sobre a tabela ``clientes``
    - VendaRepository    — operações sobre as tabelas ``vendas`` e ``venda_produto``
    - CupaoRepository    — operações sobre a tabela ``cupoes``
"""

from src.repositories.produto_repository import ProdutoRepository
from src.repositories.cliente_repository import ClienteRepository
from src.repositories.venda_repository import VendaRepository
from src.repositories.cupao_repository import CupaoRepository

__all__ = [
    "ProdutoRepository",
    "ClienteRepository",
    "VendaRepository",
    "CupaoRepository",
]
