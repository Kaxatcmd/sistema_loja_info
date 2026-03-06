#!/usr/bin/env python3
"""
Setup da Base de Dados - Versão 2
NÃO apaga dados existentes, apenas cria/atualiza tabelas
Adiciona password padrão "user123" a clientes sem password
"""

import mysql.connector
from mysql.connector import Error
import bcrypt


def hash_password(password):
    """Cria um hash seguro da password"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def setup_base_dados():
    """Cria/atualiza base de dados mantendo dados existentes"""
    
    try:
        # Conectar ao servidor MariaDB
        conexao = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            use_pure=True
        )
        
        if not conexao.is_connected():
            print("✘ Conexão ao MariaDB falhou!")
            return False
        
        cursor = conexao.cursor()
        
        # Criar base de dados se não existir
        print("▣ Verificando base de dados 'loja_informatica'...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS loja_informatica CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute("USE loja_informatica")
        conexao.commit()
        print("✔ Base de dados pronta!")
        
        # Tabela de clientes - com suporte a admin e password
        print("▥ Verificando tabela 'clientes'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id_cliente INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                telefone VARCHAR(20),
                password VARCHAR(255),
                is_admin BOOLEAN DEFAULT FALSE,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        conexao.commit()
        print("✔ Tabela 'clientes' pronta!")
        
        # Tabela de produtos
        print("▬ Verificando tabela 'produtos'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id_produto INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                descricao TEXT,
                preco DECIMAL(10,2) NOT NULL,
                stock INT DEFAULT 0,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        conexao.commit()
        print("✔ Tabela 'produtos' pronta!")
        
        # Tabela de vendas
        print("◈ Verificando tabela 'vendas'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendas (
                id_venda INT AUTO_INCREMENT PRIMARY KEY,
                id_cliente INT NOT NULL,
                data DATE NOT NULL,
                total DECIMAL(10,2) NOT NULL,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        conexao.commit()
        print("✔ Tabela 'vendas' pronta!")
        
        # Tabela de itens de venda
        print("▸ Verificando tabela 'venda_produto'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS venda_produto (
                id_venda_produto INT AUTO_INCREMENT PRIMARY KEY,
                id_venda INT NOT NULL,
                id_produto INT NOT NULL,
                preco DECIMAL(10,2) NOT NULL,
                quantidade INT DEFAULT 1,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_venda) REFERENCES vendas(id_venda) ON DELETE CASCADE,
                FOREIGN KEY (id_produto) REFERENCES produtos(id_produto) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        conexao.commit()
        print("✔ Tabela 'venda_produto' pronta!")
        
        # Adicionar password padrão aos clientes que não têm
        print("\n◆ Adicionando password padrão aos clientes existentes...")
        password_hash = hash_password("user123")
        
        cursor.execute("UPDATE clientes SET password = %s WHERE password IS NULL OR password = ''", (password_hash,))
        clientes_atualizados = cursor.rowcount
        conexao.commit()
        
        if clientes_atualizados > 0:
            print(f"✔ {clientes_atualizados} cliente(s) atualizado(s) com password padrão: user123")
        else:
            print("ⓘ Todos os clientes já têm password")
        
        # Definir João Silva como admin (se existir)
        print("\n▲ Configurando administrador...")
        cursor.execute("UPDATE clientes SET is_admin = TRUE WHERE nome = 'João Silva' OR nome = 'joao silva' OR email = 'joao@example.com'")
        conexao.commit()
        
        if cursor.rowcount > 0:
            print("✔ João Silva definido como administrador")
        
        # Adicionar produtos (apenas se tabela estiver vazia)
        cursor.execute("SELECT COUNT(*) FROM produtos")
        quantidade_produtos = cursor.fetchone()[0]
        
        if quantidade_produtos == 0:
            print("\n⬇ Adicionando produtos de exemplo...")
            produtos_exemplo = [
                ("Portátil Dell XPS 13", "Portátil de alto desempenho", 999.99, 5),
                ("Monitor LG 27\"", "Monitor 4K Ultra HD", 349.99, 8),
                ("Rato Logitech MX", "Rato sem fio de precisão", 99.99, 15),
                ("Teclado Mecânico Corsair", "Teclado RGB com switches mecânicos", 189.99, 12),
                ("Webcam 4K HD", "Câmara web profissional", 129.99, 6),
                ("Hub USB-C 7em1", "Adaptador multifuncional", 59.99, 20),
                ("Fone Bluetooth Sony", "Auscultadores sem fio com cancelamento de ruído", 279.99, 10),
                ("SSD 1TB Samsung 990 Pro", "Disco SSD NVMe ultrarrápido", 149.99, 25),
                ("Memória RAM 16GB", "Módulo DDR4 3200MHz", 79.99, 18),
                ("Placa Gráfica RTX 4060", "Placa gráfica NVIDIA", 299.99, 3),
            ]
            
            for nome, descricao, preco, stock in produtos_exemplo:
                cursor.execute(
                    "INSERT INTO produtos (nome, descricao, preco, stock) VALUES (%s, %s, %s, %s)",
                    (nome, descricao, preco, stock)
                )
            
            conexao.commit()
            print(f"✔ {len(produtos_exemplo)} produtos de exemplo inseridos!")
        else:
            print(f"ⓘ Tabela de produtos já tem {quantidade_produtos} produto(s)")
        
        # Criar índices se não existirem
        print("\n★ Otimizando base de dados...")
        try:
            cursor.execute("CREATE INDEX idx_cliente_email ON clientes(email)")
        except:
            pass  # Índice já existe
        
        try:
            cursor.execute("CREATE INDEX idx_venda_cliente ON vendas(id_cliente)")
        except:
            pass
        
        try:
            cursor.execute("CREATE INDEX idx_venda_data ON vendas(data)")
        except:
            pass
        
        conexao.commit()
        print("✔ Índices otimizados!")
        
        # Resumo final
        print("\n" + "="*50)
        print("✔ BASE DE DADOS CONFIGURADA COM SUCESSO!")
        print("="*50)
        print("\nPassword padrão para todos os clientes:")
        print("  ◉ user123")
        print("\nAdministrador:")
        print("  ▲ João Silva (joao@example.com)")
        
        # Listar clientes existentes
        cursor.execute("SELECT id_cliente, nome, email, is_admin FROM clientes")
        clientes = cursor.fetchall()
        
        print(f"\nClientes registados ({len(clientes)}):")
        for cli in clientes:
            admin = "▲" if cli[3] else "◦"
            print(f"  • {cli[1]} ({cli[2]}) - {admin}")
        
        print("\n" + "="*50)
        
        cursor.close()
        conexao.close()
        return True
        
    except Error as e:
        print(f"✘ Falha na configuração da BD: {e}")
        return False


if __name__ == '__main__':
    print("\n" + "="*50)
    print("⚙ CONFIGURAÇÃO DA BASE DE DADOS")
    print("="*50 + "\n")
    
    if setup_base_dados():
        print("\n✔ Setup concluído com sucesso!")
        print("\nProximos passos:")
        print("  1. python system_loja_informatica.py")
        print("  2. Login como cliente ou admin")
    else:
        print("\n✘ Setup falhou!")
