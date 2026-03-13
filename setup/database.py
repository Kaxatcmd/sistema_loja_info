"""
Setup de Base de Dados
Script para inicializar e configurar a BD MariaDB
"""

import mysql.connector
from mysql.connector import Error
from src.utils.security import hash_password


def criar_base_dados():
    """Cria base de dados e tabelas"""
    try:
        # Conectar sem BD especificada
        conexao = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            use_pure=True
        )
        
        cursor = conexao.cursor()
        
        # Criar BD se não existir
        cursor.execute("CREATE DATABASE IF NOT EXISTS loja_informatica")
        print("✔ Base de dados 'loja_informatica' verificada/criada")
        
        # Usar BD
        cursor.execute("USE loja_informatica")
        
        # Criar tabela clientes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id_cliente INT PRIMARY KEY AUTO_INCREMENT,
                nome VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                telefone VARCHAR(20),
                password VARCHAR(255) NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("✔ Tabela 'clientes' verificada/criada")
        
        # Criar tabela produtos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id_produto INT PRIMARY KEY AUTO_INCREMENT,
                nome VARCHAR(100) NOT NULL,
                descricao TEXT,
                preco DECIMAL(10, 2) NOT NULL,
                stock INT DEFAULT 0,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("✔ Tabela 'produtos' verificada/criada")
        
        # Criar tabela vendas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendas (
                id_venda INT PRIMARY KEY AUTO_INCREMENT,
                id_cliente INT NOT NULL,
                data DATE NOT NULL,
                total DECIMAL(10, 2) NOT NULL,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("✔ Tabela 'vendas' verificada/criada")
        
        # Criar tabela venda_produto (relação muitos-para-muitos)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS venda_produto (
                id_venda_produto INT PRIMARY KEY AUTO_INCREMENT,
                id_venda INT NOT NULL,
                id_produto INT NOT NULL,
                preco DECIMAL(10, 2) NOT NULL,
                quantidade INT NOT NULL,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_venda) REFERENCES vendas(id_venda),
                FOREIGN KEY (id_produto) REFERENCES produtos(id_produto)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("✔ Tabela 'venda_produto' verificada/criada")
        
        # Criar tabela avaliacoes (avaliações de produtos pelos clientes)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS avaliacoes (
                id_avaliacao INT PRIMARY KEY AUTO_INCREMENT,
                id_cliente INT NOT NULL,
                id_produto INT NOT NULL,
                estrelas TINYINT NOT NULL CHECK (estrelas BETWEEN 1 AND 5),
                data_avaliacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY uq_cliente_produto (id_cliente, id_produto),
                FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
                FOREIGN KEY (id_produto) REFERENCES produtos(id_produto)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("✔ Tabela 'avaliacoes' verificada/criada")
        
        # Criar índices
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_cliente_email 
            ON clientes(email)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_produto_nome 
            ON produtos(nome)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_venda_cliente 
            ON vendas(id_cliente)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_venda_produto_venda 
            ON venda_produto(id_venda)
        """)
        print("✔ Índices de BD criados")
        
        # Inserir admin se não existir
        cursor.execute("SELECT * FROM clientes WHERE email = %s", ('admin@example.com',))
        if not cursor.fetchone():
            admin_password = hash_password('admin123')
            cursor.execute("""
                INSERT INTO clientes (nome, email, password, is_admin) 
                VALUES (%s, %s, %s, %s)
            """, ('Administrador', 'admin@example.com', admin_password, True))
            conexao.commit()
            print("✔ Utilizador administrador criado")
            print("   Email: admin@example.com")
            print("   Password: admin123")
        
        # Inserir cliente teste se não existir
        cursor.execute("SELECT * FROM clientes WHERE email = %s", ('cliente@example.com',))
        if not cursor.fetchone():
            client_password = hash_password('user123')
            cursor.execute("""
                INSERT INTO clientes (nome, email, password, is_admin) 
                VALUES (%s, %s, %s, %s)
            """, ('Cliente Teste', 'cliente@example.com', client_password, False))
            conexao.commit()
            print("✔ Utilizador cliente criado")
            print("   Email: cliente@example.com")
            print("   Password: user123")
        
        cursor.close()
        conexao.close()
        
        print("\n✔ Setup de base de dados completo!")
        return True
        
    except Error as e:
        print(f"✘ Erro: {e}")
        return False


if __name__ == '__main__':
    criar_base_dados()
