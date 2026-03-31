"""
Testes Unitários — src/models/cliente.py e src/models/produto.py

Cobre:
  - Criação de instâncias com e sem parâmetros
  - ``from_dict()`` — construção a partir de dicionário da BD
  - ``__repr__()`` — representação textual
  - ``to_dict()`` — serialização (implementado na Melhoria 6)
"""

from src.models.cliente import Cliente
from src.models.produto import Produto


# ======================================================================
# Modelo Cliente
# ======================================================================

class TestCliente:
    """Testes para o modelo ``Cliente``."""

    def test_criacao_com_todos_os_campos(self):
        """Deve criar instância com todos os campos preenchidos."""
        cliente = Cliente(
            id_cliente=1,
            nome="Maria Costa",
            email="maria@exemplo.pt",
            telefone="912000001",
            password="hash_bcrypt",
            is_admin=False,
        )
        assert cliente.id_cliente == 1
        assert cliente.nome == "Maria Costa"
        assert cliente.email == "maria@exemplo.pt"
        assert cliente.telefone == "912000001"
        assert cliente.password == "hash_bcrypt"
        assert cliente.is_admin is False

    def test_criacao_valores_padrao(self):
        """Instância sem argumentos deve ter campos None/False por omissão."""
        cliente = Cliente()
        assert cliente.id_cliente is None
        assert cliente.nome is None
        assert cliente.email is None
        assert cliente.is_admin is False

    def test_from_dict_completo(self):
        """``from_dict`` deve mapear correctamente todos os campos."""
        dados = {
            "id_cliente": 5,
            "nome": "João Ferreira",
            "email": "joao@exemplo.pt",
            "telefone": "913000002",
            "password": "$2b$12$hash",
            "is_admin": True,
            "data_criacao": "2026-01-15",
        }
        cliente = Cliente.from_dict(dados)
        assert cliente.id_cliente == 5
        assert cliente.nome == "João Ferreira"
        assert cliente.email == "joao@exemplo.pt"
        assert cliente.is_admin is True
        assert cliente.data_criacao == "2026-01-15"

    def test_from_dict_campos_em_falta(self):
        """``from_dict`` com dicionário parcial deve usar valores por omissão."""
        cliente = Cliente.from_dict({"nome": "Teste"})
        assert cliente.nome == "Teste"
        assert cliente.email is None
        assert cliente.is_admin is False

    def test_from_dict_vazio(self):
        """``from_dict`` com dicionário vazio deve criar instância com tudo None."""
        cliente = Cliente.from_dict({})
        assert cliente.id_cliente is None
        assert cliente.nome is None

    def test_repr_contem_campos_chave(self):
        """``__repr__`` deve incluir id, nome, email e is_admin."""
        cliente = Cliente(id_cliente=3, nome="Ana", email="ana@x.pt", is_admin=False)
        representacao = repr(cliente)
        assert "3" in representacao
        assert "Ana" in representacao
        assert "ana@x.pt" in representacao

    def test_repr_e_string(self):
        """``__repr__`` deve devolver uma string."""
        assert isinstance(repr(Cliente()), str)

    def test_to_dict_devolve_dicionario(self):
        """``to_dict()`` deve devolver um dicionário com todos os campos."""
        cliente = Cliente(id_cliente=1, nome="X", email="x@x.pt")
        resultado = cliente.to_dict()
        assert isinstance(resultado, dict)
        assert resultado["id_cliente"] == 1
        assert resultado["nome"] == "X"
        assert resultado["email"] == "x@x.pt"


# ======================================================================
# Modelo Produto
# ======================================================================

class TestProduto:
    """Testes para o modelo ``Produto``."""

    def test_criacao_com_todos_os_campos(self):
        """Deve criar instância com todos os campos preenchidos."""
        produto = Produto(
            id_produto=10,
            nome="Webcam HD",
            descricao="1080p 30fps",
            preco=59.90,
            stock=25,
        )
        assert produto.id_produto == 10
        assert produto.nome == "Webcam HD"
        assert produto.descricao == "1080p 30fps"
        assert produto.preco == 59.90
        assert produto.stock == 25

    def test_criacao_valores_padrao(self):
        """Instância sem argumentos deve ter campos None por omissão."""
        produto = Produto()
        assert produto.id_produto is None
        assert produto.nome is None
        assert produto.preco is None
        assert produto.stock is None

    def test_from_dict_completo(self):
        """``from_dict`` deve mapear correctamente todos os campos."""
        dados = {
            "id_produto": 7,
            "nome": "SSD 1TB",
            "descricao": "NVMe M.2",
            "preco": 89.99,
            "stock": 15,
            "data_criacao": "2026-02-01",
        }
        produto = Produto.from_dict(dados)
        assert produto.id_produto == 7
        assert produto.nome == "SSD 1TB"
        assert produto.preco == 89.99
        assert produto.stock == 15

    def test_from_dict_campos_em_falta(self):
        """``from_dict`` com dicionário parcial deve usar None."""
        produto = Produto.from_dict({"nome": "Genérico"})
        assert produto.nome == "Genérico"
        assert produto.preco is None
        assert produto.stock is None

    def test_from_dict_vazio(self):
        """``from_dict`` vazio deve criar instância totalmente em None."""
        produto = Produto.from_dict({})
        assert produto.id_produto is None
        assert produto.nome is None

    def test_repr_contem_campos_chave(self):
        """``__repr__`` deve incluir id, nome, preco e stock."""
        produto = Produto(id_produto=2, nome="RAM 16GB", preco=45.0, stock=8)
        representacao = repr(produto)
        assert "2" in representacao
        assert "RAM 16GB" in representacao
        assert "45" in representacao
        assert "8" in representacao

    def test_repr_e_string(self):
        """``__repr__`` deve devolver uma string."""
        assert isinstance(repr(Produto()), str)

    def test_to_dict_devolve_dicionario(self):
        """``to_dict()`` deve devolver um dicionário com todos os campos."""
        produto = Produto(id_produto=5, nome="GPU", preco=499.0, stock=3)
        resultado = produto.to_dict()
        assert isinstance(resultado, dict)
        assert resultado["id_produto"] == 5
        assert resultado["nome"] == "GPU"
        assert resultado["preco"] == 499.0
