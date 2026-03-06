"""
Testes de Validação - Sistema de Loja
Valida funcionalidades principales do sistema
"""

import unittest
import mysql.connector
from mysql.connector import Error


class TestConexaoDB(unittest.TestCase):
    """Testa conexão à base de dados"""
    
    def test_conexao_mariadb(self):
        """Verifica se consegue conectar ao MariaDB"""
        try:
            conexao = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='loja_informatica'
            )
            self.assertTrue(conexao.is_connected())
            conexao.close()
        except Error as e:
            self.fail(f"Conexão falhada: {e}")
    
    def test_tabelas_existem(self):
        """Verifica se todas as tabelas foram criadas"""
        try:
            conexao = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='loja_informatica'
            )
            cursor = conexao.cursor()
            
            tabelas_esperadas = ['clientes', 'produtos', 'vendas', 'venda_produto']
            
            cursor.execute("SHOW TABLES")
            tabelas = [tabela[0] for tabela in cursor.fetchall()]
            
            for tabela in tabelas_esperadas:
                self.assertIn(tabela, tabelas, f"Tabela {tabela} não encontrada")
            
            cursor.close()
            conexao.close()
        except Error as e:
            self.fail(f"Erro ao verificar tabelas: {e}")


class TestValidacoes(unittest.TestCase):
    """Testa validações de entrada"""
    
    def test_validacao_email(self):
        """Testa validação de formato de email"""
        import re
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        # Emails válidos
        emails_validos = [
            'joao@example.com',
            'maria.silva@empresa.pt',
            'user+tag@domain.co.uk'
        ]
        
        for email in emails_validos:
            self.assertIsNotNone(re.match(pattern, email), 
                               f"Email válido '{email}' rejeitado")
        
        # Emails inválidos
        emails_invalidos = [
            'joao@',
            '@example.com',
            'joao.example.com',
            'joao @example.com'
        ]
        
        for email in emails_invalidos:
            self.assertIsNone(re.match(pattern, email),
                            f"Email inválido '{email}' aceito")
    
    def test_validacao_telefone(self):
        """Testa validação de telefone"""
        
        # Telefones válidos (9+ dígitos)
        telefones_validos = ['912345678', '9123456789', '919876543']
        
        for telefone in telefones_validos:
            resultado = len(telefone) >= 9 and telefone.isdigit()
            self.assertTrue(resultado, f"Telefone válido '{telefone}' rejeitado")
        
        # Telefones inválidos
        telefones_invalidos = ['91234567', '91234567a', '+351912345678', '91 234 567 8']
        
        for telefone in telefones_invalidos:
            resultado = len(telefone) >= 9 and telefone.isdigit()
            self.assertFalse(resultado, f"Telefone inválido '{telefone}' aceito")


class TestOperacoesBD(unittest.TestCase):
    """Testa operações básicas na BD"""
    
    def setUp(self):
        """Prepara conexão para testes"""
        self.conexao = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='loja_informatica'
        )
    
    def tearDown(self):
        """Fecha conexão após testes"""
        if self.conexao.is_connected():
            self.conexao.close()
    
    def test_leitura_clientes(self):
        """Testa leitura de clientes"""
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute("SELECT * FROM clientes")
        clientes = cursor.fetchall()
        cursor.close()
        
        self.assertGreater(len(clientes), 0, "Nenhum cliente encontrado")
    
    def test_leitura_produtos(self):
        """Testa leitura de produtos"""
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute("SELECT * FROM produtos")
        produtos = cursor.fetchall()
        cursor.close()
        
        self.assertGreater(len(produtos), 0, "Nenhum produto encontrado")
        
        # Verificar se produtos têm os campos esperados
        if produtos:
            produto = produtos[0]
            self.assertIn('id_produto', produto)
            self.assertIn('nome', produto)
            self.assertIn('preco', produto)
            self.assertIn('stock', produto)
    
    def test_insercao_cliente(self):
        """Testa inserção de novo cliente"""
        cursor = self.conexao.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO clientes (nome, email, telefone) VALUES (%s, %s, %s)",
                ("Cliente Teste", f"teste_{__import__('time').time()}@test.com", "912345678")
            )
            self.conexao.commit()
            
            id_novo = cursor.lastrowid
            self.assertGreater(id_novo, 0, "ID do novo cliente inválido")
            
            # Verificar se foi realmente inserido
            cursor.execute("SELECT * FROM clientes WHERE id_cliente = %s", (id_novo,))
            cliente = cursor.fetchone()
            self.assertIsNotNone(cliente, "Cliente não foi inserido")
            
        finally:
            cursor.close()


def suite_rapida():
    """Suite de testes rápidos"""
    suite = unittest.TestSuite()
    suite.addTest(TestConexaoDB('test_conexao_mariadb'))
    suite.addTest(TestValidacoes('test_validacao_email'))
    suite.addTest(TestValidacoes('test_validacao_telefone'))
    return suite


def suite_completa():
    """Suite de testes completos"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestConexaoDB))
    suite.addTests(loader.loadTestsFromTestCase(TestValidacoes))
    suite.addTests(loader.loadTestsFromTestCase(TestOperacoesBD))
    
    return suite


if __name__ == '__main__':
    import sys
    
    print("=" * 50)
    print("TESTES - SISTEMA DE LOJA DE INFORMÁTICA")
    print("=" * 50)
    print()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--completo':
        print("◈ Executando suite COMPLETA de testes...\n")
        runner = unittest.TextTestRunner(verbosity=2)
        resultado = runner.run(suite_completa())
    else:
        print("◈ Executando suite RÁPIDA de testes...\n")
        print("(Use --completo para testes mais extensivos)\n")
        runner = unittest.TextTestRunner(verbosity=2)
        resultado = runner.run(suite_rapida())
    
    print()
    print("=" * 50)
    if resultado.wasSuccessful():
        print("✓ TODOS OS TESTES PASSARAM!")
    else:
        print("✗ ALGUNS TESTES FALHARAM!")
    print("=" * 50)
