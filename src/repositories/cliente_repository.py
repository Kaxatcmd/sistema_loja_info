"""
Repositório de Clientes.

Encapsula todos os acessos à tabela ``clientes``.
Nunca devolve o campo ``password`` em listagens gerais — apenas em
``buscar_por_email``, necessário para o processo de autenticação.
"""

from src.database import DatabaseManager
from src.models.cliente import Cliente
from src.exceptions import DatabaseError


class ClienteRepository:
    """Repositório responsável pelas operações CRUD na tabela ``clientes``."""

    def __init__(self, db: DatabaseManager):
        """
        Inicializa o repositório com uma instância de DatabaseManager.

        Args:
            db (DatabaseManager): Instância já conectada ao servidor de BD.
        """
        self.db = db

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------

    def listar_todos(self) -> list[Cliente]:
        """
        Devolve todos os clientes (sem o campo password) ordenados por ID.

        Returns:
            list[Cliente]: Lista de clientes (pode ser vazia).

        Raises:
            DatabaseError: Se ocorrer um erro de BD.
        """
        linhas = self.db.executar_query(
            """
            SELECT id_cliente, nome, email, telefone,
                   is_admin, data_criacao
              FROM clientes
             ORDER BY id_cliente
            """
        )
        return [Cliente.from_dict(linha) for linha in (linhas or [])]

    def buscar_por_email(self, email: str) -> Cliente | None:
        """
        Devolve o cliente com o email fornecido ou ``None`` se não existir.

        Inclui o campo ``password`` (hash) para uso no processo de
        autenticação. Não utilizar para listagens gerais.

        Args:
            email (str): Email a pesquisar.

        Returns:
            Cliente | None: Cliente encontrado ou None.

        Raises:
            DatabaseError: Se ocorrer um erro de BD.
        """
        linhas = self.db.executar_query(
            "SELECT * FROM clientes WHERE email = %s",
            (email,)
        )
        if not linhas:
            return None
        return Cliente.from_dict(linhas[0])

    def buscar_por_id(self, id_cliente: int) -> Cliente | None:
        """
        Devolve o cliente com o ID fornecido ou ``None`` se não existir.

        Args:
            id_cliente (int): Identificador único do cliente.

        Returns:
            Cliente | None: Cliente encontrado ou None.

        Raises:
            DatabaseError: Se ocorrer um erro de BD.
        """
        linhas = self.db.executar_query(
            """
            SELECT id_cliente, nome, email, telefone,
                   is_admin, data_criacao
              FROM clientes
             WHERE id_cliente = %s
            """,
            (id_cliente,)
        )
        if not linhas:
            return None
        return Cliente.from_dict(linhas[0])

    # ------------------------------------------------------------------
    # Escrita
    # ------------------------------------------------------------------

    def criar(self, cliente: Cliente) -> Cliente:
        """
        Insere um novo cliente na BD e devolve a instância com o ID gerado.

        O campo ``cliente.password`` deve conter o hash bcrypt antes de
        chamar este método — nunca a palavra-passe em texto claro.

        Args:
            cliente (Cliente): Cliente a inserir (``id_cliente`` deve ser None).

        Returns:
            Cliente: O mesmo objecto com ``id_cliente`` preenchido.

        Raises:
            DatabaseError: Se ocorrer um erro de BD (ex.: email duplicado).
        """
        novo_id = self.db.executar_update(
            """
            INSERT INTO clientes (nome, email, telefone, password, is_admin)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                cliente.nome,
                cliente.email,
                cliente.telefone,
                cliente.password,
                bool(cliente.is_admin),
            )
        )
        cliente.id_cliente = novo_id
        return cliente

    def atualizar(self, cliente: Cliente) -> None:
        """
        Actualiza os dados de um cliente existente (excluindo a password).

        Para alterar a password utilize um método dedicado (ex.: alterar_password).

        Args:
            cliente (Cliente): Cliente com os novos valores.
                               O campo ``id_cliente`` deve estar preenchido.

        Raises:
            DatabaseError: Se ocorrer um erro de BD.
            ValueError: Se ``id_cliente`` for None.
        """
        if cliente.id_cliente is None:
            raise ValueError("id_cliente não pode ser None para actualizar.")

        self.db.executar_update(
            """
            UPDATE clientes
               SET nome     = %s,
                   email    = %s,
                   telefone = %s
             WHERE id_cliente = %s
            """,
            (cliente.nome, cliente.email, cliente.telefone, cliente.id_cliente)
        )
