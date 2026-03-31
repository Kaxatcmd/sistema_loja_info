"""
Fixtures partilhadas entre todos os testes.

Este módulo é carregado automaticamente pelo pytest antes de qualquer
teste. Define:

- ``bd_memoria`` — DatabaseManager ligado a uma BD SQLite in-memory
  com o esquema completo criado (produtos, clientes, vendas, …).
- ``produto_mock`` / ``cliente_mock`` — instâncias simples para testes
  unitários que não precisam de BD.
- ``produto_bd`` / ``cliente_bd`` — instâncias persistidas na BD
  in-memory, prontas para testes de integração.
"""

import sqlite3
import pytest

from src.database import DatabaseManager
from src.models.cliente import Cliente
from src.models.produto import Produto
from src.utils.security import hash_password


# ======================================================================
# Helpers internos
# ======================================================================

def _criar_schema(conn: sqlite3.Connection) -> None:
    """Cria o esquema completo da aplicação numa ligação SQLite."""
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS clientes (
            id_cliente   INTEGER PRIMARY KEY AUTOINCREMENT,
            nome         TEXT    NOT NULL,
            email        TEXT    UNIQUE NOT NULL,
            telefone     TEXT,
            password     TEXT    NOT NULL,
            is_admin     INTEGER DEFAULT 0,
            data_criacao TEXT    DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS produtos (
            id_produto   INTEGER PRIMARY KEY AUTOINCREMENT,
            nome         TEXT    NOT NULL,
            descricao    TEXT,
            preco        REAL    NOT NULL,
            stock        INTEGER DEFAULT 0,
            data_criacao TEXT    DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS vendas (
            id_venda     INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente   INTEGER NOT NULL,
            data         TEXT    NOT NULL,
            total        REAL    NOT NULL,
            data_criacao TEXT    DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
        );

        CREATE TABLE IF NOT EXISTS venda_produto (
            id_venda_produto INTEGER PRIMARY KEY AUTOINCREMENT,
            id_venda         INTEGER NOT NULL,
            id_produto       INTEGER NOT NULL,
            preco            REAL    NOT NULL,
            quantidade       INTEGER NOT NULL,
            data_criacao     TEXT    DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_venda)    REFERENCES vendas(id_venda),
            FOREIGN KEY (id_produto)  REFERENCES produtos(id_produto)
        );

        CREATE TABLE IF NOT EXISTS cupoes (
            id_cupao      INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo        TEXT    UNIQUE NOT NULL,
            desconto      REAL    NOT NULL,
            tipo          TEXT    NOT NULL DEFAULT 'percentagem',
            ativo         INTEGER DEFAULT 1,
            data_validade TEXT,
            data_criacao  TEXT    DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()


class _SqliteAdapter:
    """
    Adaptador que expõe a mesma interface de ``DatabaseManager``
    mas usa uma ligação SQLite in-memory.

    Permite reutilizar os repositórios (ProdutoRepository, etc.) nos
    testes sem necessitar de um servidor MariaDB.
    """

    def __init__(self) -> None:
        # Ligação persistente em memória — partilhada por todos os cursores
        self._conn = sqlite3.connect(":memory:", check_same_thread=False)
        self._conn.row_factory = sqlite3.Row      # resultados como dict-like
        _criar_schema(self._conn)
        self.connection = self._conn              # compatibilidade com DatabaseManager

    # ------------------------------------------------------------------
    # API compatível com DatabaseManager
    # ------------------------------------------------------------------

    def conectar(self) -> bool:  # noqa: D401
        """Ligação já aberta; devolve True por compatibilidade."""
        return True

    def desconectar(self) -> None:
        """Fecha a ligação SQLite."""
        self._conn.close()

    def executar_query(self, query: str, params=None) -> list[dict]:
        """
        Executa um SELECT e devolve lista de dicionários.

        Converte os marcadores ``%s`` do estilo MySQL em ``?`` (SQLite).
        """
        query_sqlite = query.replace("%s", "?")
        cursor = self._conn.cursor()
        cursor.execute(query_sqlite, params or ())
        linhas = cursor.fetchall()
        # Converter sqlite3.Row → dict simples
        return [dict(linha) for linha in linhas]

    def executar_update(self, query: str, params=None) -> int:
        """
        Executa INSERT/UPDATE/DELETE e devolve o lastrowid.

        Converte marcadores ``%s`` → ``?``.
        """
        query_sqlite = query.replace("%s", "?")
        cursor = self._conn.cursor()
        cursor.execute(query_sqlite, params or ())
        self._conn.commit()
        return cursor.lastrowid


# ======================================================================
# Fixtures
# ======================================================================

@pytest.fixture
def bd_memoria():
    """
    Fixture que fornece um adaptador SQLite in-memory com o esquema
    completo e dados limpos para cada teste.

    Âmbito: ``function`` (nova BD por teste).
    """
    adaptador = _SqliteAdapter()
    yield adaptador
    adaptador.desconectar()


# ------------------------------------------------------------------
# Dados mock — sem BD
# ------------------------------------------------------------------

@pytest.fixture
def produto_mock() -> Produto:
    """Produto simples para testes unitários (sem persistência)."""
    return Produto(
        id_produto=1,
        nome="Teclado Mecânico",
        descricao="Switch Cherry MX Blue",
        preco=79.99,
        stock=10,
    )


@pytest.fixture
def cliente_mock() -> Cliente:
    """Cliente simples para testes unitários (sem persistência)."""
    return Cliente(
        id_cliente=1,
        nome="Ana Silva",
        email="ana@exemplo.pt",
        telefone="912345678",
        password=hash_password("senha123"),
        is_admin=False,
    )


@pytest.fixture
def admin_mock() -> Cliente:
    """Cliente administrador para testes unitários."""
    return Cliente(
        id_cliente=2,
        nome="Admin Sistema",
        email="admin@exemplo.pt",
        telefone=None,
        password=hash_password("admin456"),
        is_admin=True,
    )


# ------------------------------------------------------------------
# Dados persistidos na BD in-memory — para testes de integração
# ------------------------------------------------------------------

@pytest.fixture
def produto_bd(bd_memoria) -> Produto:
    """
    Produto inserido na BD in-memory.

    Depende de ``bd_memoria``; devolve a instância com ``id_produto``
    preenchido.
    """
    bd_memoria.executar_update(
        "INSERT INTO produtos (nome, descricao, preco, stock) VALUES (?, ?, ?, ?)",
        ("Monitor 4K", "27 polegadas IPS", 349.99, 5),
    )
    linhas = bd_memoria.executar_query(
        "SELECT * FROM produtos WHERE nome = ?", ("Monitor 4K",)
    )
    return Produto.from_dict(linhas[0])


@pytest.fixture
def cliente_bd(bd_memoria) -> Cliente:
    """
    Cliente inserido na BD in-memory.

    A password é armazenada como hash bcrypt (igual à produção).
    """
    password_hash = hash_password("teste123")
    bd_memoria.executar_update(
        "INSERT INTO clientes (nome, email, telefone, password, is_admin) VALUES (?, ?, ?, ?, ?)",
        ("Carlos Mendes", "carlos@teste.pt", "913000001", password_hash, 0),
    )
    linhas = bd_memoria.executar_query(
        "SELECT * FROM clientes WHERE email = ?", ("carlos@teste.pt",)
    )
    return Cliente.from_dict(linhas[0])
