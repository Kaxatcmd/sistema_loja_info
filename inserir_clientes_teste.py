#!/usr/bin/env python3
"""
Inserir clientes de teste para a loja
Password padrão: user123
"""

import mysql.connector
from mysql.connector import Error
import bcrypt


def hash_password(password):
    """Hash da password"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


try:
    conexao = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='loja_informatica',
        use_pure=True
    )
    
    cursor = conexao.cursor()
    password_hash = hash_password("user123")
    
    clientes_exemplo = [
        ("João Silva", "joao@example.com", "912345678", password_hash, True),
        ("Maria Santos", "maria@example.com", "913456789", password_hash, False),
        ("Pedro Oliveira", "pedro@example.com", "914567890", password_hash, False),
        ("Ana Costa", "ana@example.com", "915678901", password_hash, False),
        ("Carlos Ferreira", "carlos@example.com", "916789012", password_hash, False),
    ]
    
    print("Inserindo clientes de teste...")
    
    for nome, email, tfone, pwd, admin in clientes_exemplo:
        try:
            cursor.execute(
                "INSERT INTO clientes (nome, email, telefone, password, is_admin) VALUES (%s, %s, %s, %s, %s)",
                (nome, email, tfone, pwd, admin)
            )
            tipo = "▲ ADMIN" if admin else "◦ Utilizador"
            print(f"✔ {nome} ({tipo})")
        except Error as e:
            if "Duplicate entry" in str(e):
                print(f"ⓘ {nome} já existe")
            else:
                raise
    
    conexao.commit()
    
    # Listar todos os clientes
    print("\nClientes cadastrados:")
    cursor.execute("SELECT id_cliente, nome, email, is_admin FROM clientes ORDER BY is_admin DESC, nome ASC")
    for row in cursor.fetchall():
        admin = "▲ ADMIN" if row[3] else "◦ Utilizador"
        print(f"  {row[0]:2d}. {row[1]:<20} {row[2]:<25} {admin}")
    
    cursor.close()
    conexao.close()
    
    print("\n✓ Clientes de teste inseridos com sucesso!")
    print("\nPassword para TODOS os clientes: user123")
    
except Error as e:
    print(f"✗ Erro: {e}")
