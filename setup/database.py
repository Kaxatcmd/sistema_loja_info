"""
Setup de Base de Dados
Script para inicializar e configurar a BD MariaDB
"""

import mysql.connector
from mysql.connector import Error
from src.utils.security import hash_password
from src.utils.logger import obter_logger

logger = obter_logger(__name__)


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
        logger.info("Base de dados 'loja_informatica' verificada/criada")
        
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
        logger.info("Tabela 'clientes' verificada/criada")
        
        # Criar tabela categorias
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categorias (
                id_categoria INT PRIMARY KEY AUTO_INCREMENT,
                nome         VARCHAR(100) NOT NULL,
                descricao    TEXT,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        logger.info("Tabela 'categorias' verificada/criada")

        # Criar tabela produtos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id_produto   INT PRIMARY KEY AUTO_INCREMENT,
                id_categoria INT,
                nome         VARCHAR(100) NOT NULL,
                descricao    TEXT,
                preco        DECIMAL(10, 2) NOT NULL,
                stock        INT DEFAULT 0,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria)
                    ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        logger.info("Tabela 'produtos' verificada/criada")
        
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
        logger.info("Tabela 'vendas' verificada/criada")
        
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
        logger.info("Tabela 'venda_produto' verificada/criada")
        
        # Criar tabela cupoes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cupoes (
                id_cupao     INT PRIMARY KEY AUTO_INCREMENT,
                codigo       VARCHAR(50) UNIQUE NOT NULL,
                desconto     DECIMAL(10, 2) NOT NULL,
                tipo         ENUM('percentagem', 'fixo') NOT NULL DEFAULT 'percentagem',
                ativo        BOOLEAN DEFAULT TRUE,
                data_validade DATE,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        logger.info("Tabela 'cupoes' verificada/criada")

        # Criar tabela avaliacoes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS avaliacoes (
                id_avaliacao INT PRIMARY KEY AUTO_INCREMENT,
                id_cliente   INT NOT NULL,
                id_produto   INT NOT NULL,
                nota         TINYINT NOT NULL CHECK (nota BETWEEN 1 AND 5),
                comentario   TEXT,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
                FOREIGN KEY (id_produto) REFERENCES produtos(id_produto),
                UNIQUE KEY uq_avaliacao (id_cliente, id_produto)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        logger.info("Tabela 'avaliacoes' verificada/criada")

        # Criar tabela wishlist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wishlist (
                id_wishlist  INT PRIMARY KEY AUTO_INCREMENT,
                id_cliente   INT NOT NULL,
                id_produto   INT NOT NULL,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
                FOREIGN KEY (id_produto) REFERENCES produtos(id_produto),
                UNIQUE KEY uq_wishlist (id_cliente, id_produto)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        logger.info("Tabela 'wishlist' verificada/criada")

        # ── Migração: adicionar id_categoria a produtos se ainda não existir ──
        cursor.execute("""
            SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = 'loja_informatica'
              AND TABLE_NAME   = 'produtos'
              AND COLUMN_NAME  = 'id_categoria'
        """)
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "ALTER TABLE produtos ADD COLUMN id_categoria INT AFTER id_produto"
            )
            # Verificar se FK já existe antes de a criar
            cursor.execute("""
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
                WHERE TABLE_SCHEMA    = 'loja_informatica'
                  AND TABLE_NAME      = 'produtos'
                  AND CONSTRAINT_NAME = 'fk_produto_categoria'
                  AND CONSTRAINT_TYPE = 'FOREIGN KEY'
            """)
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    ALTER TABLE produtos
                    ADD CONSTRAINT fk_produto_categoria
                    FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria)
                    ON DELETE SET NULL
                """)
            conexao.commit()
            logger.info("Migração: coluna 'id_categoria' adicionada à tabela 'produtos'")
        else:
            logger.info("Migração: 'id_categoria' já existe em 'produtos' — nada a fazer")

        # ── Migração: garantir que clientes.telefone é nullable ─────────────
        cursor.execute("""
            SELECT IS_NULLABLE FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = 'loja_informatica'
              AND TABLE_NAME   = 'clientes'
              AND COLUMN_NAME  = 'telefone'
        """)
        row = cursor.fetchone()
        if row and row[0] == 'NO':
            cursor.execute(
                "ALTER TABLE clientes MODIFY telefone VARCHAR(20) DEFAULT NULL"
            )
            conexao.commit()
            logger.info("Migração: 'clientes.telefone' tornado nullable")

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
            CREATE INDEX IF NOT EXISTS idx_produto_categoria
            ON produtos(id_categoria)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_venda_cliente 
            ON vendas(id_cliente)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_venda_produto_venda 
            ON venda_produto(id_venda)
        """)
        logger.info("Índices de BD criados")
        # Inserir categorias padrão se tabela estiver vazia
        cursor.execute("SELECT COUNT(*) FROM categorias")
        if cursor.fetchone()[0] == 0:
            categorias_padrao = [
                ('Portáteis',    'Computadores portáteis e ultrabooks'),
                ('Monitores',    'Monitores e écrans de computador'),
                ('Impressoras',  'Impressoras, scanners e multifunções'),
                ('Periféricos',  'Teclados, ratos, auscultadores e outros periféricos'),
                ('Armazenamento','Discos SSD, HDD, pendrives e cartões de memória'),
                ('Componentes',  'Processadores, placas gráficas, memória RAM e motherboards'),
                ('Networking',   'Routers, switches, placas de rede e cabos'),
                ('Software',     'Sistemas operativos, licenças e aplicações'),
                ('Outros',       'Produtos informáticos diversos'),
            ]
            for nome_cat, desc_cat in categorias_padrao:
                cursor.execute(
                    "INSERT INTO categorias (nome, descricao) VALUES (%s, %s)",
                    (nome_cat, desc_cat)
                )
            conexao.commit()
            logger.info("Categorias padrão inseridas (%d)", len(categorias_padrao))

        # Inserir produtos de demonstração se tabela estiver vazia
        cursor.execute("SELECT COUNT(*) FROM produtos")
        if cursor.fetchone()[0] == 0:
            cursor.execute("SELECT id_categoria, nome FROM categorias")
            cats = {nome: cid for cid, nome in cursor.fetchall()}
            produtos_demo = [
                # Portáteis
                (cats['Portáteis'], 'Portátil Dell XPS 13',        'Intel i7, 16GB RAM, 512GB SSD, 13.4" OLED',              1199.99, 5),
                (cats['Portáteis'], 'MacBook Air M3 13"',           'Portátil Apple com chip M3, 8GB RAM, 256GB SSD',          1299.99, 6),
                (cats['Portáteis'], 'HP Pavilion 15 FHD',           'Intel i5-1335U, 16GB RAM, 512GB SSD',                     749.99,  8),
                (cats['Portáteis'], 'ASUS VivoBook 16X',             'Ryzen 5 7530U, 16GB RAM, 512GB SSD',                      649.99, 10),
                (cats['Portáteis'], 'Acer Swift 3',                  'Ultrafino Intel i7, 16GB RAM, 1TB SSD',                    899.99,  5),
                (cats['Portáteis'], 'Lenovo IdeaPad Slim 5',         'Intel i5, 8GB RAM, 512GB SSD, Full HD',                   599.99,  7),
                (cats['Portáteis'], 'PC Laptop Lenovo Thinkpad 15',  'Lenovo ThinkPad 15, Intel i7, 16GB RAM, 1TB SSD',        1099.99,  4),
                # Monitores
                (cats['Monitores'], 'Monitor LG 27"',                'IPS Full HD 27", 75Hz, FreeSync, HDMI',                   299.99,  8),
                (cats['Monitores'], 'Samsung Odyssey G5 27"',        'Monitor curvo QHD 165Hz, 1ms, FreeSync Premium',          399.99,  9),
                (cats['Monitores'], 'Dell UltraSharp U2723D',        'IPS 4K 27", USB-C 90W, sRGB 100%',                        649.99,  5),
                (cats['Monitores'], 'BenQ PD2705U',                  'Monitor 4K 27" para design, USB-C, IPS',                  549.99,  4),
                (cats['Monitores'], 'AOC 24G2SPU',                   'Monitor IPS 24" FHD 165Hz, 1ms, FreeSync',                199.99, 12),
                (cats['Monitores'], 'LG UltraWide 34WP65G',          'Monitor UltraWide 34" IPS 75Hz, FreeSync, USB-C',         449.99,  6),
                # Impressoras
                (cats['Impressoras'], 'Epson EcoTank ET-2870',       'Multifunções sem tinteiros, WiFi',                        299.99,  8),
                (cats['Impressoras'], 'HP LaserJet Pro MFP M234dw',  'Laser monocromática, duplex, WiFi',                       249.99,  6),
                (cats['Impressoras'], 'Brother DCP-L3560CDW',        'Laser cor multifunções, WiFi, duplex',                    449.99,  4),
                (cats['Impressoras'], 'Canon MAXIFY GX5050',         'Jato de tinta de alta capacidade, WiFi',                  329.99,  5),
                (cats['Impressoras'], 'Epson WorkForce WF-7840',     'A3 multifunções, WiFi, Ethernet',                         549.99,  3),
                # Periféricos
                (cats['Periféricos'], 'Rato Logitech MX Master 3S', 'Rato sem fios ergonómico, 8000 DPI, silencioso',           99.99, 12),
                (cats['Periféricos'], 'Teclado Mecânico Corsair K95','Teclado gaming mecânico RGB, Cherry MX Speed',            179.99,  8),
                (cats['Periféricos'], 'Webcam 4K HD',                'Webcam USB 4K com microfone estéreo incorporado',          79.99,  6),
                (cats['Periféricos'], 'Fone Bluetooth Sony',         'Auscultadores on-ear, 30h bateria, SBC/AAC',              149.99, 10),
                (cats['Periféricos'], 'Hub USB-C 7em1',              'Hub USB-C com HDMI, USB-A 3.0, SD, PD 100W',              49.99, 17),
                (cats['Periféricos'], 'Logitech MX Keys S',          'Teclado sem fios premium, retroiluminado',                109.99, 15),
                (cats['Periféricos'], 'Razer DeathAdder V3 Pro',     'Rato gaming sem fios 30000 DPI, ergonómico',              149.99, 10),
                (cats['Periféricos'], 'Sony WH-1000XM5',             'Auscultadores ANC, 30h bateria, Bluetooth',               349.99,  8),
                (cats['Periféricos'], 'Logitech Brio 4K',            'Webcam 4K Ultra HD, HDR, Windows Hello',                  199.99,  9),
                (cats['Periféricos'], 'Anker USB-C Hub 10em1',       'Hub USB-C HDMI 4K, SD, USB-A, Ethernet, PD 100W',          79.99, 20),
                # Armazenamento
                (cats['Armazenamento'], 'SSD 1TB Samsung 990 Pro',   'NVMe PCIe 4.0, 7450MB/s leitura',                        129.99,  9),
                (cats['Armazenamento'], 'Memória RAM 16GB',           'DDR4 3200MHz, CL16, compatível AMD/Intel',                 59.99, 17),
                (cats['Armazenamento'], 'WD Black SN850X 2TB',       'SSD NVMe PCIe 4.0, 7300MB/s, PS5 compatível',            189.99,  8),
                (cats['Armazenamento'], 'Seagate BarraCuda 4TB HDD', 'Disco rígido interno 4TB, 5400rpm, SATA III',              89.99, 10),
                (cats['Armazenamento'], 'Samsung T7 Shield 1TB',     'SSD externo portátil USB 3.2, resistente a choques',      109.99, 12),
                (cats['Armazenamento'], 'Crucial MX500 1TB SATA',    'SSD SATA 2.5" 560MB/s, upgrade de portátil',              79.99, 15),
                (cats['Armazenamento'], 'SanDisk 256GB USB-C',       'Pendrive USB-C + USB-A 3.2 Ultra Dual Drive Go',           19.99, 30),
                # Componentes
                (cats['Componentes'], 'Placa Gráfica RTX 4060',      'NVIDIA RTX 4060 8GB GDDR6, DLSS 3, Ray Tracing',         399.99,  6),
                (cats['Componentes'], 'Intel Core i9-14900K',        'Processador 24-core, 5.8GHz turbo, LGA1700',             589.99,  5),
                (cats['Componentes'], 'AMD Radeon RX 7800 XT',       'Placa gráfica 16GB GDDR6, RDNA 3',                       499.99,  6),
                (cats['Componentes'], 'Corsair Vengeance 32GB DDR5', 'Kit RAM DDR5 6000MHz CL36, 2×16GB',                      119.99, 10),
                (cats['Componentes'], 'ASUS ROG Strix B650E-F',      'Motherboard AMD AM5, DDR5, PCIe 5.0, WiFi 6E',           329.99,  4),
                (cats['Componentes'], 'Cooler Master Hyper 212',     'Cooler CPU TDP 150W, fan 120mm PWM',                      39.99, 18),
                # Networking
                (cats['Networking'], 'TP-Link Archer AX73 WiFi 6',  'Router WiFi 6 AX5400, 6 antenas, MU-MIMO',               149.99,  8),
                (cats['Networking'], 'Netgear GS308 Switch 8P',      'Switch Gigabit 8 portas, Plug & Play',                    39.99, 15),
                (cats['Networking'], 'TP-Link TL-PA9020P AV2000',   'Kit PLC Powerline 2000Mbps, 2 tomadas AC',                 79.99,  9),
                (cats['Networking'], 'Ubiquiti UniFi AP U6 Lite',    'Access Point WiFi 6, dual-band',                         129.99,  6),
                (cats['Networking'], 'Cable Matters Cat6A 10m',      'Cabo Ethernet Cat6a 10Gbps, blindado',                    12.99, 50),
                # Software
                (cats['Software'], 'Microsoft 365 Personal 1 ano',  'Word, Excel, PowerPoint, 1TB OneDrive',                   69.99, 25),
                (cats['Software'], 'Windows 11 Pro OEM',             'Sistema operativo Windows 11 Pro, licença OEM',          149.99, 20),
                (cats['Software'], 'Adobe Creative Cloud 1 ano',     'Photoshop, Illustrator, Premiere, After Effects',        599.99,  8),
                (cats['Software'], 'Kaspersky Plus 3 PCs 1 ano',     'Antivírus, VPN ilimitada, Password Manager',              49.99, 30),
                (cats['Software'], 'Corel VideoStudio 2024',         'Editor de vídeo, exportação 4K, efeitos',                 79.99, 12),
                # Outros
                (cats['Outros'], 'Suporte Monitor Duplo Ergonómico', 'Braço duplo ajustável, 2×9kg, VESA 75/100',               79.99, 10),
                (cats['Outros'], 'Filtro de Picos 6 Tomadas',        'Proteção contra sobretensões, cabo 1.5m',                 24.99, 20),
                (cats['Outros'], 'Pasta Térmica Noctua NT-H2',       'Pasta térmica premium 3.5g, -50ºC a 210ºC',              12.99, 35),
                (cats['Outros'], 'Cooling Pad Laptop 17"',           'Base de arrefecimento 2 fans, USB, altura ajustável',     29.99, 14),
                (cats['Outros'], 'Tela de Privacidade 14"',          'Filtro anti-espião para portátil 14"',                    39.99, 16),
            ]
            for p in produtos_demo:
                cursor.execute(
                    "INSERT INTO produtos (id_categoria, nome, descricao, preco, stock) VALUES (%s, %s, %s, %s, %s)",
                    p
                )
            conexao.commit()
            logger.info("Produtos de demonstração inseridos (%d)", len(produtos_demo))

        # Inserir admin se não existir
        cursor.execute("SELECT * FROM clientes WHERE email = %s", ('admin@example.com',))
        if not cursor.fetchone():
            admin_password = hash_password('admin123')
            cursor.execute("""
                INSERT INTO clientes (nome, email, password, is_admin) 
                VALUES (%s, %s, %s, %s)
            """, ('Administrador', 'admin@example.com', admin_password, True))
            conexao.commit()
            logger.info("Utilizador administrador criado — Email: admin@example.com")
            logger.info("Credenciais iniciais do admin registadas no log — altere a password após o primeiro login")
        
        # Inserir cliente teste se não existir
        cursor.execute("SELECT * FROM clientes WHERE email = %s", ('cliente@example.com',))
        if not cursor.fetchone():
            client_password = hash_password('user123')
            cursor.execute("""
                INSERT INTO clientes (nome, email, password, is_admin) 
                VALUES (%s, %s, %s, %s)
            """, ('Cliente Teste', 'cliente@example.com', client_password, False))
            conexao.commit()
            logger.info("Utilizador cliente de teste criado — Email: cliente@example.com")
        
        cursor.close()
        conexao.close()
        
        logger.info("Setup de base de dados concluído com sucesso")
        return True
        
    except Error as e:
        logger.error("Erro durante o setup de BD: %s", e)
        return False


if __name__ == '__main__':
    criar_base_dados()
