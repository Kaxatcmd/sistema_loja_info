"""
Gerenciamento de Base de Dados.

Classe DatabaseManager para operações com MariaDB.
Classe PooledDatabaseManager para operações com pool de conexões.

Erros de BD são comunicados através de ``DatabaseError``; a camada de
UI é responsável por capturar essa exceção e apresentar o erro ao
utilizador — sem qualquer dependência de tkinter neste módulo.
"""

import mysql.connector
import mysql.connector.pooling
from mysql.connector import Error
from src.config import DATABASE_CONFIG, DB_POOL_SIZE
from src.exceptions import DatabaseError
from src.utils.logger import obter_logger

logger = obter_logger(__name__)


class DatabaseManager:
    """Gere a conexão e operações de baixo nível com MariaDB."""

    def __init__(self, config=None):
        """
        Inicializa o gerenciador de BD.

        Args:
            config (dict): Configuração da BD (host, user, password, database).
                           Se não fornecido, usa DATABASE_CONFIG de src/config.py.
        """
        if config is None:
            config = DATABASE_CONFIG

        self.host = config.get('host', 'localhost')
        self.user = config.get('user', 'root')
        self.password = config.get('password', '')
        self.database = config.get('database', 'loja_informatica')
        self.connection = None

    def conectar(self):
        """
        Estabelece conexão com a base de dados.

        Returns:
            bool: True quando a conexão é bem-sucedida.

        Raises:
            DatabaseError: Se não for possível ligar ao servidor de BD.
        """
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                use_pure=True
            )
            return self.connection.is_connected()
        except Error as e:
            raise DatabaseError(f"Erro de conexão: {e}") from e

    def desconectar(self):
        """Fecha a conexão com a base de dados, se estiver aberta."""
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def executar_query(self, query, params=None):
        """
        Executa um SELECT na base de dados.

        Args:
            query (str): Comando SQL SELECT.
            params (tuple): Parâmetros para prepared statement.

        Returns:
            list[dict]: Lista de dicionários com os resultados.

        Raises:
            DatabaseError: Se ocorrer um erro durante a execução da query.
        """
        try:
            cursor = self.connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            resultado = cursor.fetchall()
            cursor.close()
            return resultado
        except Error as e:
            raise DatabaseError(str(e)) from e

    def executar_update(self, query, params=None):
        """
        Executa um INSERT, UPDATE ou DELETE na base de dados.

        Args:
            query (str): Comando SQL INSERT/UPDATE/DELETE.
            params (tuple): Parâmetros para prepared statement.

        Returns:
            int: ID da última linha inserida (lastrowid).

        Raises:
            DatabaseError: Se ocorrer um erro; a transação é revertida
                           automaticamente antes de lançar a exceção.
        """
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            resultado = cursor.lastrowid
            cursor.close()
            return resultado
        except Error as e:
            self.connection.rollback()
            raise DatabaseError(str(e)) from e


# ---------------------------------------------------------------------------
# Pool de conexões
# ---------------------------------------------------------------------------


class PooledDatabaseManager:
    """
    Gerenciador de BD com pool de conexões MariaDB.

    Utiliza ``mysql.connector.pooling.MySQLConnectionPool`` para manter
    um conjunto de conexões reutilizáveis.  Cada operação pede uma
    conexão ao pool, executa o SQL e devolve a conexão ao pool
    imediatamente a seguir — sem manter uma conexão aberta permanente.

    A interface pública é idêntica à de ``DatabaseManager``, pelo que
    pode ser usada de forma transparente por todos os repositórios e
    serviços.

    Exemplo::

        db = PooledDatabaseManager()
        db.conectar()
        resultados = db.executar_query("SELECT * FROM produtos")
        db.desconectar()
    """

    def __init__(self, config: dict | None = None, pool_size: int | None = None) -> None:
        """
        Args:
            config:    Dicionário de configuração da BD.  Se omitido,
                       usa ``DATABASE_CONFIG`` de ``src/config.py``.
            pool_size: Número máximo de conexões no pool.  Se omitido,
                       usa ``DB_POOL_SIZE`` de ``src/config.py``.
        """
        self._config = config if config is not None else DATABASE_CONFIG
        self._pool_size = pool_size if pool_size is not None else DB_POOL_SIZE
        self._pool: mysql.connector.pooling.MySQLConnectionPool | None = None

    # ------------------------------------------------------------------
    # Ciclo de vida
    # ------------------------------------------------------------------

    def conectar(self) -> bool:
        """
        Cria o pool de conexões.

        Returns:
            True se o pool foi criado com sucesso.

        Raises:
            DatabaseError: Se não for possível criar o pool.
        """
        try:
            self._pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="loja_pool",
                pool_size=self._pool_size,
                host=self._config.get('host', 'localhost'),
                user=self._config.get('user', 'root'),
                password=self._config.get('password', ''),
                database=self._config.get('database', 'loja_informatica'),
                use_pure=True,
            )
            logger.info("Pool de conexões criado (tamanho=%d).", self._pool_size)
            return True
        except Error as e:
            raise DatabaseError(f"Erro ao criar pool de conexões: {e}") from e

    def desconectar(self) -> None:
        """
        Liberta a referência ao pool.

        O ``mysql-connector-python`` não expõe um método de fecho
        explícito do pool; basta remover a referência para que o GC
        limpe as conexões inactivas.
        """
        self._pool = None
        logger.info("Referência ao pool de conexões removida.")

    # ------------------------------------------------------------------
    # Operações de leitura
    # ------------------------------------------------------------------

    def executar_query(self, query: str, params=None) -> list[dict]:
        """
        Executa um SELECT usando uma conexão do pool.

        A conexão é devolvida ao pool automaticamente após a execução.

        Args:
            query:  Comando SQL SELECT (com marcadores ``%s``).
            params: Tuplo/lista de parâmetros.

        Returns:
            Lista de dicionários com os resultados.

        Raises:
            DatabaseError: Se o pool não estiver iniciado ou ocorrer
                           um erro na BD.
        """
        if self._pool is None:
            raise DatabaseError("Pool não inicializado. Chame conectar() primeiro.")
        conn = None
        try:
            conn = self._pool.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params or ())
            resultado = cursor.fetchall()
            cursor.close()
            return resultado
        except Error as e:
            raise DatabaseError(str(e)) from e
        finally:
            if conn is not None:
                conn.close()  # devolve ao pool

    # ------------------------------------------------------------------
    # Operações de escrita
    # ------------------------------------------------------------------

    def executar_update(self, query: str, params=None) -> int:
        """
        Executa um INSERT/UPDATE/DELETE usando uma conexão do pool.

        A transação é confirmada antes de devolver a conexão ao pool.
        Em caso de erro, é feito rollback.

        Args:
            query:  Comando SQL (com marcadores ``%s``).
            params: Tuplo/lista de parâmetros.

        Returns:
            ID da última linha inserida (lastrowid).

        Raises:
            DatabaseError: Se o pool não estiver iniciado ou ocorrer
                           um erro na BD.
        """
        if self._pool is None:
            raise DatabaseError("Pool não inicializado. Chame conectar() primeiro.")
        conn = None
        try:
            conn = self._pool.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            conn.commit()
            resultado = cursor.lastrowid
            cursor.close()
            return resultado
        except Error as e:
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
            raise DatabaseError(str(e)) from e
        finally:
            if conn is not None:
                conn.close()  # devolve ao pool

    # ------------------------------------------------------------------
    # Propriedade informativa
    # ------------------------------------------------------------------

    @property
    def pool_size(self) -> int:
        """Tamanho configurado para o pool."""
        return self._pool_size

