"""
Testes de Integração — src/repositories/

Testa todos os repositórios usando a fixture ``bd_memoria`` (SQLite
in-memory definida em ``tests/conftest.py``). Nenhum servidor MariaDB
é necessário.

Cobertura:
  - ProdutoRepository:  listar_todos, buscar_por_id, buscar_por_nome,
                        criar, atualizar, deletar, atualizar_stock
  - ClienteRepository:  listar_todos, buscar_por_email, buscar_por_id,
                        criar, atualizar
  - VendaRepository:    criar_venda, historico_cliente, historico_geral,
                        total_vendas_periodo, criar_venda sem itens
"""

import pytest
from datetime import date

from src.repositories.produto_repository import ProdutoRepository
from src.repositories.cliente_repository import ClienteRepository
from src.repositories.venda_repository import VendaRepository
from src.models.produto import Produto
from src.models.cliente import Cliente
from src.utils.security import hash_password


# ======================================================================
# ProdutoRepository
# ======================================================================

class TestProdutoRepository:
    """Testes de integração para ``ProdutoRepository``."""

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _inserir_produto(self, bd, nome="Rato USB", preco=15.0, stock=20):
        """Insere um produto directamente na BD e devolve o ID gerado."""
        id_ = bd.executar_update(
            "INSERT INTO produtos (nome, descricao, preco, stock) VALUES (?, ?, ?, ?)",
            (nome, "desc", preco, stock),
        )
        return id_

    # ------------------------------------------------------------------
    # listar_todos
    # ------------------------------------------------------------------

    def test_listar_todos_bd_vazia(self, bd_memoria):
        """Lista vazia quando não há produtos na BD."""
        repo = ProdutoRepository(bd_memoria)
        assert repo.listar_todos() == []

    def test_listar_todos_devolve_todos(self, bd_memoria):
        """Deve devolver todos os produtos inseridos."""
        self._inserir_produto(bd_memoria, nome="Produto A")
        self._inserir_produto(bd_memoria, nome="Produto B")
        repo = ProdutoRepository(bd_memoria)
        resultado = repo.listar_todos()
        assert len(resultado) == 2

    def test_listar_todos_ordem_alfabetica(self, bd_memoria):
        """Produtos devem ser devolvidos por ordem alfabética de nome."""
        self._inserir_produto(bd_memoria, nome="Zebra")
        self._inserir_produto(bd_memoria, nome="Ábaco")
        repo = ProdutoRepository(bd_memoria)
        nomes = [p.nome for p in repo.listar_todos()]
        assert nomes == sorted(nomes)

    def test_listar_todos_devolve_instancias_produto(self, bd_memoria):
        """Cada elemento da lista deve ser uma instância de ``Produto``."""
        self._inserir_produto(bd_memoria)
        repo = ProdutoRepository(bd_memoria)
        for item in repo.listar_todos():
            assert isinstance(item, Produto)

    # ------------------------------------------------------------------
    # buscar_por_id
    # ------------------------------------------------------------------

    def test_buscar_por_id_existente(self, bd_memoria):
        """Deve devolver o produto correcto quando o ID existe."""
        id_ = self._inserir_produto(bd_memoria, nome="SSD 512GB", preco=89.0)
        repo = ProdutoRepository(bd_memoria)
        produto = repo.buscar_por_id(id_)
        assert produto is not None
        assert produto.nome == "SSD 512GB"
        assert produto.preco == 89.0

    def test_buscar_por_id_inexistente(self, bd_memoria):
        """Deve devolver None quando o ID não existe."""
        repo = ProdutoRepository(bd_memoria)
        assert repo.buscar_por_id(9999) is None

    # ------------------------------------------------------------------
    # buscar_por_nome
    # ------------------------------------------------------------------

    def test_buscar_por_nome_correspondencia_parcial(self, bd_memoria):
        """Pesquisa parcial deve encontrar produtos que contêm o texto."""
        self._inserir_produto(bd_memoria, nome="Teclado Mecânico RGB")
        self._inserir_produto(bd_memoria, nome="Teclado Membrana")
        self._inserir_produto(bd_memoria, nome="Rato Óptico")
        repo = ProdutoRepository(bd_memoria)
        resultado = repo.buscar_por_nome("Teclado")
        assert len(resultado) == 2

    def test_buscar_por_nome_sem_resultados(self, bd_memoria):
        """Deve devolver lista vazia quando não há correspondência."""
        self._inserir_produto(bd_memoria, nome="Monitor 4K")
        repo = ProdutoRepository(bd_memoria)
        assert repo.buscar_por_nome("inexistente") == []

    # ------------------------------------------------------------------
    # criar
    # ------------------------------------------------------------------

    def test_criar_produto_devolve_id(self, bd_memoria):
        """``criar`` deve preencher ``id_produto`` na instância devolvida."""
        repo = ProdutoRepository(bd_memoria)
        novo = Produto(nome="Hub USB-C", descricao="7 portas", preco=29.99, stock=50)
        resultado = repo.criar(novo)
        assert resultado.id_produto is not None
        assert resultado.id_produto > 0

    def test_criar_produto_persiste_na_bd(self, bd_memoria):
        """Produto criado deve ser recuperável pela BD."""
        repo = ProdutoRepository(bd_memoria)
        novo = Produto(nome="Webcam 1080p", preco=49.0, stock=10)
        repo.criar(novo)
        encontrado = repo.buscar_por_nome("Webcam")
        assert len(encontrado) == 1
        assert encontrado[0].preco == 49.0

    def test_criar_multiplos_produtos_ids_unicos(self, bd_memoria):
        """IDs atribuídos a produtos criados devem ser únicos."""
        repo = ProdutoRepository(bd_memoria)
        p1 = repo.criar(Produto(nome="P1", preco=1.0, stock=1))
        p2 = repo.criar(Produto(nome="P2", preco=2.0, stock=2))
        assert p1.id_produto != p2.id_produto

    # ------------------------------------------------------------------
    # atualizar
    # ------------------------------------------------------------------

    def test_atualizar_produto(self, bd_memoria):
        """Actualização deve alterar os campos na BD."""
        id_ = self._inserir_produto(bd_memoria, nome="GPU Antiga", preco=200.0, stock=3)
        repo = ProdutoRepository(bd_memoria)
        produto = repo.buscar_por_id(id_)
        produto.nome = "GPU Nova"
        produto.preco = 350.0
        repo.atualizar(produto)
        actualizado = repo.buscar_por_id(id_)
        assert actualizado.nome == "GPU Nova"
        assert actualizado.preco == 350.0

    def test_atualizar_sem_id_lanca_valueerror(self, bd_memoria):
        """``atualizar`` sem ``id_produto`` deve lançar ``ValueError``."""
        repo = ProdutoRepository(bd_memoria)
        produto_sem_id = Produto(nome="Sem ID", preco=10.0, stock=1)
        with pytest.raises(ValueError, match="id_produto"):
            repo.atualizar(produto_sem_id)

    # ------------------------------------------------------------------
    # deletar
    # ------------------------------------------------------------------

    def test_deletar_produto(self, bd_memoria):
        """Produto deletado não deve ser encontrado depois."""
        id_ = self._inserir_produto(bd_memoria, nome="A Remover")
        repo = ProdutoRepository(bd_memoria)
        repo.deletar(id_)
        assert repo.buscar_por_id(id_) is None

    def test_deletar_nao_afeta_outros_produtos(self, bd_memoria):
        """Deletar um produto não deve remover os outros."""
        id1 = self._inserir_produto(bd_memoria, nome="Manter")
        id2 = self._inserir_produto(bd_memoria, nome="Remover")
        repo = ProdutoRepository(bd_memoria)
        repo.deletar(id2)
        assert repo.buscar_por_id(id1) is not None

    # ------------------------------------------------------------------
    # atualizar_stock
    # ------------------------------------------------------------------

    def test_atualizar_stock_incrementar(self, bd_memoria):
        """Stock deve aumentar com valor positivo."""
        id_ = self._inserir_produto(bd_memoria, stock=10)
        repo = ProdutoRepository(bd_memoria)
        repo.atualizar_stock(id_, 5)
        assert repo.buscar_por_id(id_).stock == 15

    def test_atualizar_stock_decrementar(self, bd_memoria):
        """Stock deve diminuir com valor negativo (venda)."""
        id_ = self._inserir_produto(bd_memoria, stock=10)
        repo = ProdutoRepository(bd_memoria)
        repo.atualizar_stock(id_, -3)
        assert repo.buscar_por_id(id_).stock == 7


# ======================================================================
# ClienteRepository
# ======================================================================

class TestClienteRepository:
    """Testes de integração para ``ClienteRepository``."""

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _inserir_cliente(self, bd, nome="Teste User",
                         email="teste@exemplo.pt", is_admin=0):
        """Insere um cliente directamente na BD e devolve o ID gerado."""
        return bd.executar_update(
            "INSERT INTO clientes (nome, email, telefone, password, is_admin) "
            "VALUES (?, ?, ?, ?, ?)",
            (nome, email, "900000000", hash_password("pass123"), is_admin),
        )

    # ------------------------------------------------------------------
    # listar_todos
    # ------------------------------------------------------------------

    def test_listar_todos_bd_vazia(self, bd_memoria):
        """Lista vazia quando não há clientes na BD."""
        repo = ClienteRepository(bd_memoria)
        assert repo.listar_todos() == []

    def test_listar_todos_devolve_clientes(self, bd_memoria):
        """Deve devolver todos os clientes inseridos."""
        self._inserir_cliente(bd_memoria, nome="Ana", email="ana@t.pt")
        self._inserir_cliente(bd_memoria, nome="Beto", email="beto@t.pt")
        repo = ClienteRepository(bd_memoria)
        assert len(repo.listar_todos()) == 2

    def test_listar_todos_nao_inclui_password(self, bd_memoria):
        """Campo ``password`` não deve estar presente nos clientes listados."""
        self._inserir_cliente(bd_memoria)
        repo = ClienteRepository(bd_memoria)
        clientes = repo.listar_todos()
        assert len(clientes) == 1
        # O campo password deve ser None (não seleccionado na query)
        assert clientes[0].password is None

    def test_listar_todos_devolve_instancias_cliente(self, bd_memoria):
        """Cada elemento deve ser instância de ``Cliente``."""
        self._inserir_cliente(bd_memoria)
        repo = ClienteRepository(bd_memoria)
        for item in repo.listar_todos():
            assert isinstance(item, Cliente)

    # ------------------------------------------------------------------
    # buscar_por_email
    # ------------------------------------------------------------------

    def test_buscar_por_email_existente(self, bd_memoria):
        """Deve devolver o cliente correcto quando o email existe."""
        self._inserir_cliente(bd_memoria, nome="Carlos", email="carlos@t.pt")
        repo = ClienteRepository(bd_memoria)
        cliente = repo.buscar_por_email("carlos@t.pt")
        assert cliente is not None
        assert cliente.nome == "Carlos"

    def test_buscar_por_email_inclui_password(self, bd_memoria):
        """``buscar_por_email`` deve incluir o hash da password (para autenticação)."""
        self._inserir_cliente(bd_memoria, email="hash@t.pt")
        repo = ClienteRepository(bd_memoria)
        cliente = repo.buscar_por_email("hash@t.pt")
        assert cliente.password is not None
        assert cliente.password.startswith("$2b$") or cliente.password.startswith("$2a$")

    def test_buscar_por_email_inexistente(self, bd_memoria):
        """Deve devolver None quando o email não existe."""
        repo = ClienteRepository(bd_memoria)
        assert repo.buscar_por_email("nao@existe.pt") is None

    # ------------------------------------------------------------------
    # buscar_por_id
    # ------------------------------------------------------------------

    def test_buscar_por_id_existente(self, bd_memoria):
        """Deve devolver o cliente correcto quando o ID existe."""
        id_ = self._inserir_cliente(bd_memoria, nome="Diana", email="diana@t.pt")
        repo = ClienteRepository(bd_memoria)
        cliente = repo.buscar_por_id(id_)
        assert cliente is not None
        assert cliente.nome == "Diana"

    def test_buscar_por_id_inexistente(self, bd_memoria):
        """Deve devolver None quando o ID não existe."""
        repo = ClienteRepository(bd_memoria)
        assert repo.buscar_por_id(9999) is None

    # ------------------------------------------------------------------
    # criar
    # ------------------------------------------------------------------

    def test_criar_cliente_devolve_id(self, bd_memoria):
        """``criar`` deve preencher ``id_cliente`` na instância devolvida."""
        repo = ClienteRepository(bd_memoria)
        novo = Cliente(
            nome="Eva",
            email="eva@t.pt",
            telefone="911000001",
            password=hash_password("eva123"),
            is_admin=False,
        )
        resultado = repo.criar(novo)
        assert resultado.id_cliente is not None
        assert resultado.id_cliente > 0

    def test_criar_cliente_persiste_na_bd(self, bd_memoria):
        """Cliente criado deve ser recuperável por email."""
        repo = ClienteRepository(bd_memoria)
        novo = Cliente(
            nome="Fábio",
            email="fabio@t.pt",
            password=hash_password("fab456"),
        )
        repo.criar(novo)
        encontrado = repo.buscar_por_email("fabio@t.pt")
        assert encontrado is not None
        assert encontrado.nome == "Fábio"

    def test_criar_admin(self, bd_memoria):
        """Deve ser possível criar um cliente administrador."""
        repo = ClienteRepository(bd_memoria)
        admin = Cliente(
            nome="Admin",
            email="admin@t.pt",
            password=hash_password("adm789"),
            is_admin=True,
        )
        repo.criar(admin)
        encontrado = repo.buscar_por_email("admin@t.pt")
        # SQLite devolve 0/1; coerce para bool
        assert bool(encontrado.is_admin) is True

    # ------------------------------------------------------------------
    # atualizar
    # ------------------------------------------------------------------

    def test_atualizar_cliente(self, bd_memoria):
        """Actualização deve alterar nome, email e telefone na BD."""
        id_ = self._inserir_cliente(bd_memoria, nome="Antigo", email="antigo@t.pt")
        repo = ClienteRepository(bd_memoria)
        cliente = repo.buscar_por_id(id_)
        cliente.nome = "Novo Nome"
        cliente.email = "novo@t.pt"
        cliente.telefone = "999999999"
        repo.atualizar(cliente)
        actualizado = repo.buscar_por_id(id_)
        assert actualizado.nome == "Novo Nome"
        assert actualizado.email == "novo@t.pt"
        assert actualizado.telefone == "999999999"

    def test_atualizar_sem_id_lanca_valueerror(self, bd_memoria):
        """``atualizar`` sem ``id_cliente`` deve lançar ``ValueError``."""
        repo = ClienteRepository(bd_memoria)
        cliente_sem_id = Cliente(nome="Sem ID", email="x@t.pt")
        with pytest.raises(ValueError, match="id_cliente"):
            repo.atualizar(cliente_sem_id)


# ======================================================================
# VendaRepository
# ======================================================================

class TestVendaRepository:
    """Testes de integração para ``VendaRepository``."""

    # ------------------------------------------------------------------
    # Dados auxiliares
    # ------------------------------------------------------------------

    def _criar_dados_base(self, bd):
        """Insere um cliente e dois produtos; devolve (cliente_id, [ids_produto])."""
        cliente_id = bd.executar_update(
            "INSERT INTO clientes (nome, email, password, is_admin) VALUES (?, ?, ?, ?)",
            ("Comprador", "comprador@t.pt", hash_password("c123"), 0),
        )
        p1_id = bd.executar_update(
            "INSERT INTO produtos (nome, preco, stock) VALUES (?, ?, ?)",
            ("Produto X", 10.0, 50),
        )
        p2_id = bd.executar_update(
            "INSERT INTO produtos (nome, preco, stock) VALUES (?, ?, ?)",
            ("Produto Y", 25.0, 30),
        )
        return cliente_id, [p1_id, p2_id]

    # ------------------------------------------------------------------
    # criar_venda
    # ------------------------------------------------------------------

    def test_criar_venda_devolve_id(self, bd_memoria):
        """``criar_venda`` deve devolver um ID inteiro positivo."""
        cliente_id, [p1_id, _] = self._criar_dados_base(bd_memoria)
        repo = VendaRepository(bd_memoria)
        itens = [{"id_produto": p1_id, "preco": 10.0, "quantidade": 2}]
        id_venda = repo.criar_venda(cliente_id, itens)
        assert isinstance(id_venda, int)
        assert id_venda > 0

    def test_criar_venda_persiste_cabecalho(self, bd_memoria):
        """Cabeçalho da venda deve ser pesquisável na BD."""
        cliente_id, [p1_id, _] = self._criar_dados_base(bd_memoria)
        repo = VendaRepository(bd_memoria)
        itens = [{"id_produto": p1_id, "preco": 10.0, "quantidade": 1}]
        id_venda = repo.criar_venda(cliente_id, itens)
        linhas = bd_memoria.executar_query(
            "SELECT * FROM vendas WHERE id_venda = ?", (id_venda,)
        )
        assert len(linhas) == 1
        assert float(linhas[0]["total"]) == pytest.approx(10.0)

    def test_criar_venda_persiste_itens(self, bd_memoria):
        """Itens da venda devem ser persistidos em ``venda_produto``."""
        cliente_id, [p1_id, p2_id] = self._criar_dados_base(bd_memoria)
        repo = VendaRepository(bd_memoria)
        itens = [
            {"id_produto": p1_id, "preco": 10.0, "quantidade": 1},
            {"id_produto": p2_id, "preco": 25.0, "quantidade": 2},
        ]
        id_venda = repo.criar_venda(cliente_id, itens)
        linhas = bd_memoria.executar_query(
            "SELECT * FROM venda_produto WHERE id_venda = ?", (id_venda,)
        )
        assert len(linhas) == 2

    def test_criar_venda_calcula_total_correcto(self, bd_memoria):
        """Total da venda deve ser a soma de preço × quantidade."""
        cliente_id, [p1_id, p2_id] = self._criar_dados_base(bd_memoria)
        repo = VendaRepository(bd_memoria)
        itens = [
            {"id_produto": p1_id, "preco": 10.0, "quantidade": 3},   # 30
            {"id_produto": p2_id, "preco": 25.0, "quantidade": 2},   # 50
        ]
        id_venda = repo.criar_venda(cliente_id, itens)
        linhas = bd_memoria.executar_query(
            "SELECT total FROM vendas WHERE id_venda = ?", (id_venda,)
        )
        assert float(linhas[0]["total"]) == pytest.approx(80.0)

    def test_criar_venda_decrementa_stock(self, bd_memoria):
        """``criar_venda`` deve decrementar o stock dos produtos vendidos."""
        cliente_id, [p1_id, _] = self._criar_dados_base(bd_memoria)
        repo = VendaRepository(bd_memoria)
        itens = [{"id_produto": p1_id, "preco": 10.0, "quantidade": 5}]
        repo.criar_venda(cliente_id, itens)
        linhas = bd_memoria.executar_query(
            "SELECT stock FROM produtos WHERE id_produto = ?", (p1_id,)
        )
        # Stock inicial = 50; vendeu 5 → deve ficar 45
        assert linhas[0]["stock"] == 45

    def test_criar_venda_sem_itens_lanca_valueerror(self, bd_memoria):
        """``criar_venda`` com lista vazia deve lançar ``ValueError``."""
        repo = VendaRepository(bd_memoria)
        with pytest.raises(ValueError, match="itens"):
            repo.criar_venda(1, [])

    # ------------------------------------------------------------------
    # historico_cliente
    # ------------------------------------------------------------------

    def test_historico_cliente_bd_vazia(self, bd_memoria):
        """Cliente sem compras deve devolver lista vazia."""
        repo = VendaRepository(bd_memoria)
        assert repo.historico_cliente(9999) == []

    def test_historico_cliente_devolve_compras(self, bd_memoria):
        """Deve devolver todas as compras do cliente especificado."""
        cliente_id, [p1_id, _] = self._criar_dados_base(bd_memoria)
        repo = VendaRepository(bd_memoria)
        repo.criar_venda(cliente_id, [{"id_produto": p1_id, "preco": 10.0, "quantidade": 1}])
        repo.criar_venda(cliente_id, [{"id_produto": p1_id, "preco": 10.0, "quantidade": 2}])
        historico = repo.historico_cliente(cliente_id)
        # Cada venda tem 1 item → 2 linhas no total
        assert len(historico) == 2

    def test_historico_cliente_nao_mostra_outros_clientes(self, bd_memoria):
        """Histórico de cliente A não deve incluir compras do cliente B."""
        cliente_a, [p1_id, _] = self._criar_dados_base(bd_memoria)
        cliente_b = bd_memoria.executar_update(
            "INSERT INTO clientes (nome, email, password, is_admin) VALUES (?, ?, ?, ?)",
            ("Outro", "outro@t.pt", hash_password("o123"), 0),
        )
        repo = VendaRepository(bd_memoria)
        repo.criar_venda(cliente_a, [{"id_produto": p1_id, "preco": 10.0, "quantidade": 1}])
        repo.criar_venda(cliente_b, [{"id_produto": p1_id, "preco": 10.0, "quantidade": 1}])
        historico_a = repo.historico_cliente(cliente_a)
        historico_b = repo.historico_cliente(cliente_b)
        assert len(historico_a) == 1
        assert len(historico_b) == 1

    # ------------------------------------------------------------------
    # historico_geral
    # ------------------------------------------------------------------

    def test_historico_geral_bd_vazia(self, bd_memoria):
        """Sem vendas, deve devolver lista vazia."""
        repo = VendaRepository(bd_memoria)
        assert repo.historico_geral() == []

    def test_historico_geral_devolve_todas_vendas(self, bd_memoria):
        """Deve devolver vendas de todos os clientes."""
        cliente_a, [p1_id, _] = self._criar_dados_base(bd_memoria)
        cliente_b = bd_memoria.executar_update(
            "INSERT INTO clientes (nome, email, password, is_admin) VALUES (?, ?, ?, ?)",
            ("B", "b@t.pt", hash_password("b123"), 0),
        )
        repo = VendaRepository(bd_memoria)
        repo.criar_venda(cliente_a, [{"id_produto": p1_id, "preco": 10.0, "quantidade": 1}])
        repo.criar_venda(cliente_b, [{"id_produto": p1_id, "preco": 10.0, "quantidade": 1}])
        assert len(repo.historico_geral()) == 2

    def test_historico_geral_respeita_limite(self, bd_memoria):
        """O parâmetro ``limite`` deve limitar os resultados."""
        cliente_id, [p1_id, _] = self._criar_dados_base(bd_memoria)
        repo = VendaRepository(bd_memoria)
        for _ in range(5):
            repo.criar_venda(cliente_id, [{"id_produto": p1_id, "preco": 10.0, "quantidade": 1}])
        assert len(repo.historico_geral(limite=3)) == 3

    # ------------------------------------------------------------------
    # total_vendas_periodo
    # ------------------------------------------------------------------

    def test_total_vendas_periodo_sem_vendas(self, bd_memoria):
        """Sem vendas no período, deve devolver 0.0."""
        repo = VendaRepository(bd_memoria)
        total = repo.total_vendas_periodo(date(2026, 1, 1), date(2026, 1, 31))
        assert total == pytest.approx(0.0)

    def test_total_vendas_periodo_com_vendas(self, bd_memoria):
        """Deve somar os totais das vendas no intervalo."""
        cliente_id, [p1_id, _] = self._criar_dados_base(bd_memoria)
        repo = VendaRepository(bd_memoria)
        # Cria duas vendas — a data é sempre TODAY (date.today())
        repo.criar_venda(cliente_id, [{"id_produto": p1_id, "preco": 10.0, "quantidade": 1}])
        repo.criar_venda(cliente_id, [{"id_produto": p1_id, "preco": 10.0, "quantidade": 2}])
        hoje = date.today()
        total = repo.total_vendas_periodo(hoje, hoje)
        # 1ª venda: 10€; 2ª venda: 20€ → total = 30€
        assert total == pytest.approx(30.0)
