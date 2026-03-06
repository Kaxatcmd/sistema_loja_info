#!/usr/bin/env python3
"""
Script de Teste da Aplicação Loja de Informática
Valida:
- Conexão com base de dados
- Estrutura da aplicação
- Sistema de passwords com hash
"""

import sys
import os

# Adicionar diretório ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mysql.connector
from mysql.connector import Error
import bcrypt


def testar_conexao_bd():
    """Testa a conexão com a base de dados"""
    print("\n⚙ TESTE 1: Conexão com Base de Dados")
    print("-" * 50)
    
    try:
        conexao = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='loja_informatica',
            use_pure=True
        )
        
        if conexao.is_connected():
            print("✔ Conexão estabelecida com sucesso!")
            
            # Verificar tabelas
            cursor = conexao.cursor(dictionary=True)
            cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='loja_informatica'")
            tabelas = cursor.fetchall()
            
            print(f"✔ Tabelas encontradas ({len(tabelas)}):")
            for tabela in tabelas:
                print(f"  - {tabela['TABLE_NAME']}")
            
            cursor.close()
            conexao.close()
            return True
        else:
            print("✘ Não foi possível conectar à base de dados")
            return False
            
    except Error as e:
        print(f"✘ Erro de conexão: {e}")
        print("\n◐ Dica: Certifique-se de que:")
        print("   1. MariaDB/MySQL está em execução")
        print("   2. A base de dados 'loja_informatica' existe")
        print("   3. O script setup_database.py foi executado")
        return False


def testar_hash_password():
    """Testa o sistema de hash de passwords"""
    print("\n⚙ TESTE 2: Sistema de Hash de Passwords")
    print("-" * 50)
    
    try:
        # Teste de hash
        password = "senha_teste"
        salt = bcrypt.gensalt(rounds=12)
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        
        print(f"✔ Password original: {password}")
        print(f"✔ Hash gerado: {password_hash[:50]}...")
        
        # Teste de verificação
        if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
            print("✔ Hash verificado com sucesso!")
            return True
        else:
            print("✘ Falha na verificação do hash")
            return False
            
    except Exception as e:
        print(f"✘ Erro no sistema de hash: {e}")
        return False


def testar_estrutura_arquivos():
    """Verifica a estrutura dos arquivos do projeto"""
    print("\n⚙ TESTE 3: Estrutura de Arquivos")
    print("-" * 50)
    
    arquivos_necessarios = [
        'system_loja_informatica.py',
        'setup_database.py',
        'requirements.txt',
        'README_LOJA.md'
    ]
    
    todos_existem = True
    for arquivo in arquivos_necessarios:
        caminho = os.path.join(os.path.dirname(__file__), arquivo)
        if os.path.exists(caminho):
            print(f"✔ {arquivo}")
        else:
            print(f"✘ {arquivo} - NÃO ENCONTRADO")
            todos_existem = False
    
    return todos_existem


def testar_dados_exemplo():
    """Verifica dados de exemplo na base de dados"""
    print("\n⚙ TESTE 4: Dados de Exemplo")
    print("-" * 50)
    
    try:
        conexao = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='loja_informatica',
            use_pure=True
        )
        
        if conexao.is_connected():
            cursor = conexao.cursor(dictionary=True)
            
            # Contar clientes
            cursor.execute("SELECT COUNT(*) as total FROM clientes")
            clientes = cursor.fetchone()
            print(f"✔ Clientes: {clientes['total']}")
            
            # Contar produtos
            cursor.execute("SELECT COUNT(*) as total FROM produtos")
            produtos = cursor.fetchone()
            print(f"✔ Produtos: {produtos['total']}")
            
            # Contar vendas
            cursor.execute("SELECT COUNT(*) as total FROM vendas")
            vendas = cursor.fetchone()
            print(f"✔ Vendas: {vendas['total']}")
            
            # Mostrar um produto de exemplo
            cursor.execute("SELECT * FROM produtos LIMIT 1")
            produto = cursor.fetchone()
            if produto:
                print(f"\n  Exemplo de produto:")
                print(f"    Nome: {produto['nome']}")
                print(f"    Preço: {produto['preco']:.2f}€")
                print(f"    Stock: {produto['stock']}")
            
            cursor.close()
            conexao.close()
            return True
        else:
            return False
            
    except Error as e:
        print(f"✘ Erro ao verificar dados: {e}")
        return False


def main():
    """Executa todos os testes"""
    print("\n" + "=" * 50)
    print("◈ TESTES DA APLICAÇÃO LOJA DE INFORMÁTICA")
    print("=" * 50)
    
    resultados = {
        'Conexão BD': testar_conexao_bd(),
        'Hash Password': testar_hash_password(),
        'Estrutura Arquivos': testar_estrutura_arquivos(),
        'Dados Exemplo': testar_dados_exemplo(),
    }
    
    # Resumo
    print("\n" + "=" * 50)
    print("▣ RESUMO DOS TESTES")
    print("=" * 50)
    
    for teste, resultado in resultados.items():
        status = "✔ PASSOU" if resultado else "✘ FALHOU"
        print(f"{teste}: {status}")
    
    todos_passaram = all(resultados.values())
    
    print("\n" + "=" * 50)
    if todos_passaram:
        print("✓ TODOS OS TESTES PASSARAM!")
        print("\n► Para executar a aplicação:")
        print("   python system_loja_informatica.py")
        print("\n▥ Credenciais de teste:")
        print("   Email: joao@example.com")
        print("   Password: senha123")
    else:
        print("✗ ALGUNS TESTES FALHARAM")
        print("\nVerifique os erros acima e tente resolver os problemas.")
    
    print("=" * 50 + "\n")
    
    return 0 if todos_passaram else 1


if __name__ == '__main__':
    sys.exit(main())
