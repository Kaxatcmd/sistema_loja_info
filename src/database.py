"""
Gerenciamento de Base de Dados
Classe DatabaseManager para operações com MariaDB
"""

import mysql.connector
from mysql.connector import Error
from tkinter import messagebox
from src.config import DATABASE_CONFIG


class DatabaseManager:
    """Gerencia conexão e operações com MariaDB"""
    
    def __init__(self, config=None):
        """
        Inicializa o gerenciador de BD
        
        Args:
            config (dict): Configuração da BD (host, user, password, database)
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
        Estabelece conexão com a base de dados
        
        Returns:
            bool: True se conexão bem-sucedida, False caso contrário
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
            messagebox.showerror("Erro BD", f"Erro de conexão: {e}")
            return False
    
    def desconectar(self):
        """Fecha conexão com a base de dados"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def executar_query(self, query, params=None):
        """
        Executa SELECT na base de dados
        
        Args:
            query (str): Comando SQL SELECT
            params (tuple): Parâmetros para prepared statement
            
        Returns:
            list: Lista de dicionários com resultados ou None se erro
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
            messagebox.showerror("Erro Query", str(e))
            return None
    
    def executar_update(self, query, params=None):
        """
        Executa INSERT/UPDATE/DELETE na base de dados
        
        Args:
            query (str): Comando SQL INSERT/UPDATE/DELETE
            params (tuple): Parâmetros para prepared statement
            
        Returns:
            int: Last row ID se INSERT, ou None se erro
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
            messagebox.showerror("Erro Update", str(e))
            return None
