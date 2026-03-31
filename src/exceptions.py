"""
Exceções customizadas da aplicação.

Centralizar as exceções permite que as camadas de dados (database.py,
repositories) comuniquem falhas sem depender da camada de UI.
"""


class DatabaseError(Exception):
    """
    Exceção lançada quando ocorre um erro de base de dados.

    Substitui as chamadas directas a ``tkinter.messagebox`` dentro de
    ``DatabaseManager``, desacoplando a lógica de dados da interface
    gráfica.  A UI captura esta exceção e decide como apresentar o erro
    ao utilizador (notificação, diálogo, log, etc.).

    Exemplo de uso::

        # na camada de dados
        raise DatabaseError(f"Erro de conexão: {e}")

        # na camada de UI
        try:
            self.db.conectar()
        except DatabaseError as e:
            self.notify.error(str(e))
    """
