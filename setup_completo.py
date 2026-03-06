#!/usr/bin/env python3
"""
Setup Rápido - Todos os passos em um script
Executa: Migração de admin + Inserir clientes de teste
"""

import sys
import os

# Adicionar diretório ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mysql.connector
from mysql.connector import Error
import bcrypt


def hash_password(password):
    """Hash da password"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def setup_completo():
    """Setup completo em um script"""
    
    try:
        conexao = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='loja_informatica',
            use_pure=True
        )
        
        if not conexao.is_connected():
            print("✗ Erro ao conectar ao MariaDB!")
            return False
        
        cursor = conexao.cursor()
        
        print("\n" + "="*60)
        print("⚙ SETUP COMPLETO - SISTEMA DE LOJA (TKINTER)")
        print("="*60 + "\n")
        
        # 1. Adicionar coluna is_admin (se não existir)
        print("[1]  Preparando tabela de clientes...")
        try:
            cursor.execute("ALTER TABLE clientes ADD COLUMN is_admin BOOLEAN DEFAULT FALSE")
            conexao.commit()
            print("   ✔ Coluna 'is_admin' adicionada")
        except Error as e:
            if "Duplicate column" in str(e):
                print("   ✔ Coluna 'is_admin' já existe")
            else:
                print(f"   ✘ Erro: {e}")
                return False
        
        # 2. Definir João Silva como admin E com password
        print("\n[2]  Configurando administrador...")
        password_hash = hash_password("user123")
        
        cursor.execute("UPDATE clientes SET is_admin = TRUE, password = %s WHERE nome = 'João Silva' OR email = 'joao@example.com'", (password_hash,))
        conexao.commit()
        
        if cursor.rowcount > 0:
            print(f"   ✔ João Silva definido como administrador (password: user123)")
        else:
            print("   ✘ João Silva não encontrado (será criado com outros clientes)")
        
        # 3. Inserir clientes de teste
        print("\n[3]  Inserindo clientes de teste...")
        
        clientes_exemplo = [
            ("João Silva", "joao@example.com", "912345678", password_hash, True),
            ("Maria Santos", "maria@example.com", "913456789", password_hash, False),
            ("Pedro Oliveira", "pedro@example.com", "914567890", password_hash, False),
            ("Ana Costa", "ana@example.com", "915678901", password_hash, False),
            ("Carlos Ferreira", "carlos@example.com", "916789012", password_hash, False),
        ]
        
        inseridos = 0
        existentes = 0
        
        for nome, email, tfone, pwd, admin in clientes_exemplo:
            try:
                cursor.execute(
                    "INSERT INTO clientes (nome, email, telefone, password, is_admin) VALUES (%s, %s, %s, %s, %s)",
                    (nome, email, tfone, pwd, admin)
                )
                conexao.commit()
                tipo = "▲ ADMIN" if admin else "◦ Utilizador"
                print(f"   ✔ {nome} ({tipo})")
                inseridos += 1
            except Error as e:
                if "Duplicate entry" in str(e):
                    existentes += 1
                else:
                    raise
        
        if existentes > 0:
            print(f"   ⓘ  {existentes} cliente(s) já existiam")
        
        # 4. Contar indones
        cursor.execute("SELECT SUM(stock) FROM produtos")
        stock_total = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM produtos")
        num_produtos = cursor.fetchone()[0]
        
        # 5. Resumo final
        print("\n" + "="*60)
        print("✓ SETUP CONCLUÍDO COM SUCESSO!")
        print("="*60)
        
        # Listar clientes
        print("\n▨ Clientes Cadastrados:")
        cursor.execute("SELECT id_cliente, nome, email, is_admin FROM clientes ORDER BY is_admin DESC, nome ASC")
        
        clientes = cursor.fetchall()
        for row in clientes:
            admin = "▲ ADMIN" if row[3] else "◦ User"
            print(f"   • {row[1]:<20} ({row[2]:<25}) {admin}")
        
        print(f"\n▣ Estatísticas da Loja:")
        print(f"   • Clientes: {len(clientes)}")
        print(f"   • Produtos: {num_produtos}")
        print(f"   • Stock Total: {stock_total} unidades")
        
        print(f"\n◆ Credenciais de Teste:")
        print(f"   • Password para TODOS: user123")
        print(f"   • Admin: joao@example.com")
        print(f"   • Utilizador: maria@example.com")
        
        print("\n" + "="*60)
        print("► Próximo passo:")
        print("   python sistema_loja_tkinter.py")
        print("="*60 + "\n")
        
        cursor.close()
        conexao.close()
        return True
        
    except Error as e:
        print(f"\n✗ Erro: {e}")
        return False


if __name__ == '__main__':
    success = setup_completo()
    sys.exit(0 if success else 1)
