"""
Testes unitários para PooledDatabaseManager.

Usam mocks para simular o driver mysql-connector-python — não requerem
um servidor MariaDB em execução.

Cobertura:
  - __init__: valores padrão e personalizados
  - conectar(): cria pool com os parâmetros corretos; DatabaseError em falha
  - desconectar(): remove referência ao pool
  - executar_query(): obtém conexão do pool, executa, devolve lista de dicts
  - executar_query() sem pool: DatabaseError
  - executar_update(): commit; devolve lastrowid; rollback em erro
  - executar_update() sem pool: DatabaseError
  - pool_size: propriedade informativa
"""

from unittest.mock import MagicMock, patch, call
import pytest
from mysql.connector import Error as MysqlError

from src.database import PooledDatabaseManager
from src.exceptions import DatabaseError


# ======================================================================
# Fixtures
# ======================================================================

CONFIG_TESTE = {
    "host": "localhost",
    "user": "teste",
    "password": "senha",
    "database": "test_db",
}


@pytest.fixture
def manager():
    """PooledDatabaseManager com configuração de teste (pool não criado)."""
    return PooledDatabaseManager(config=CONFIG_TESTE, pool_size=3)


@pytest.fixture
def pool_mock():
    """Mock de MySQLConnectionPool."""
    return MagicMock()


@pytest.fixture
def conn_mock():
    """Mock de uma conexão do pool."""
    conn = MagicMock()
    cursor = MagicMock()
    cursor.fetchall.return_value = [{"id": 1, "nome": "Teste"}]
    cursor.lastrowid = 42
    conn.cursor.return_value = cursor
    return conn


@pytest.fixture
def manager_com_pool(manager, pool_mock, conn_mock):
    """PooledDatabaseManager com pool já injectado."""
    pool_mock.get_connection.return_value = conn_mock
    manager._pool = pool_mock
    return manager, pool_mock, conn_mock


# ======================================================================
# __init__
# ======================================================================

class TestInit:
    def test_pool_size_personalizado(self):
        m = PooledDatabaseManager(config=CONFIG_TESTE, pool_size=7)
        assert m.pool_size == 7

    def test_pool_size_padrao_usa_config(self):
        from src.config import DB_POOL_SIZE
        m = PooledDatabaseManager()
        assert m.pool_size == DB_POOL_SIZE

    def test_pool_inicial_none(self):
        m = PooledDatabaseManager(config=CONFIG_TESTE, pool_size=2)
        assert m._pool is None

    def test_config_personalizada(self):
        m = PooledDatabaseManager(config=CONFIG_TESTE, pool_size=2)
        assert m._config == CONFIG_TESTE


# ======================================================================
# conectar
# ======================================================================

class TestConectar:
    @patch("src.database.mysql.connector.pooling.MySQLConnectionPool")
    def test_cria_pool_com_parametros_corretos(self, MockPool, manager):
        MockPool.return_value = MagicMock()
        resultado = manager.conectar()

        assert resultado is True
        MockPool.assert_called_once_with(
            pool_name="loja_pool",
            pool_size=3,
            host="localhost",
            user="teste",
            password="senha",
            database="test_db",
            use_pure=True,
        )

    @patch("src.database.mysql.connector.pooling.MySQLConnectionPool")
    def test_armazena_pool(self, MockPool, manager):
        pool_inst = MagicMock()
        MockPool.return_value = pool_inst
        manager.conectar()
        assert manager._pool is pool_inst

    @patch("src.database.mysql.connector.pooling.MySQLConnectionPool")
    def test_levanta_database_error_em_falha(self, MockPool, manager):
        MockPool.side_effect = MysqlError("conexão recusada")
        with pytest.raises(DatabaseError, match="pool"):
            manager.conectar()


# ======================================================================
# desconectar
# ======================================================================

class TestDesconectar:
    def test_define_pool_como_none(self, manager_com_pool):
        manager, pool, _ = manager_com_pool
        manager.desconectar()
        assert manager._pool is None


# ======================================================================
# executar_query
# ======================================================================

class TestExecutarQuery:
    def test_retorna_lista_de_dicts(self, manager_com_pool):
        manager, pool, conn = manager_com_pool
        resultado = manager.executar_query("SELECT * FROM produtos")
        assert resultado == [{"id": 1, "nome": "Teste"}]

    def test_pede_conexao_ao_pool(self, manager_com_pool):
        manager, pool, conn = manager_com_pool
        manager.executar_query("SELECT 1")
        pool.get_connection.assert_called_once()

    def test_devolve_conexao_ao_pool_apos_uso(self, manager_com_pool):
        manager, pool, conn = manager_com_pool
        manager.executar_query("SELECT 1")
        conn.close.assert_called()

    def test_passa_params_ao_cursor(self, manager_com_pool):
        manager, pool, conn = manager_com_pool
        manager.executar_query("SELECT * FROM produtos WHERE id=%s", (1,))
        conn.cursor().execute.assert_called_with(
            "SELECT * FROM produtos WHERE id=%s", (1,)
        )

    def test_sem_pool_levanta_database_error(self, manager):
        with pytest.raises(DatabaseError, match="Pool não inicializado"):
            manager.executar_query("SELECT 1")

    def test_erro_mysql_levanta_database_error(self, manager_com_pool):
        manager, pool, conn = manager_com_pool
        conn.cursor.return_value.execute.side_effect = MysqlError("erro query")
        with pytest.raises(DatabaseError, match="erro query"):
            manager.executar_query("SELECT 1")

    def test_conexao_devolvida_mesmo_com_erro(self, manager_com_pool):
        manager, pool, conn = manager_com_pool
        conn.cursor.return_value.execute.side_effect = MysqlError("falha")
        with pytest.raises(DatabaseError):
            manager.executar_query("SELECT 1")
        conn.close.assert_called()


# ======================================================================
# executar_update
# ======================================================================

class TestExecutarUpdate:
    def test_retorna_lastrowid(self, manager_com_pool):
        manager, pool, conn = manager_com_pool
        resultado = manager.executar_update(
            "INSERT INTO produtos (nome) VALUES (%s)", ("Teclado",)
        )
        assert resultado == 42

    def test_chama_commit(self, manager_com_pool):
        manager, pool, conn = manager_com_pool
        manager.executar_update("INSERT INTO t VALUES (%s)", (1,))
        conn.commit.assert_called_once()

    def test_devolve_conexao_ao_pool_apos_uso(self, manager_com_pool):
        manager, pool, conn = manager_com_pool
        manager.executar_update("INSERT INTO t VALUES (%s)", (1,))
        conn.close.assert_called()

    def test_sem_pool_levanta_database_error(self, manager):
        with pytest.raises(DatabaseError, match="Pool não inicializado"):
            manager.executar_update("INSERT INTO t VALUES (%s)", (1,))

    def test_erro_mysql_faz_rollback(self, manager_com_pool):
        manager, pool, conn = manager_com_pool
        conn.cursor.return_value.execute.side_effect = MysqlError("constraint")
        with pytest.raises(DatabaseError):
            manager.executar_update("INSERT INTO t VALUES (%s)", (1,))
        conn.rollback.assert_called()

    def test_erro_mysql_devolve_conexao(self, manager_com_pool):
        manager, pool, conn = manager_com_pool
        conn.cursor.return_value.execute.side_effect = MysqlError("constraint")
        with pytest.raises(DatabaseError):
            manager.executar_update("INSERT INTO t VALUES (%s)", (1,))
        conn.close.assert_called()


# ======================================================================
# pool_size property
# ======================================================================

class TestPoolSize:
    def test_devolve_valor_configurado(self, manager):
        assert manager.pool_size == 3
