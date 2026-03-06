# 🏪 LOJA DE INFORMÁTICA - SISTEMA COMPLETO V2.0

Aplicação desktop Python para gestão de loja de informática com interface gráfica (Tkinter) e base de dados MySQL/MariaDB.

---

## 📋 Visão Geral

### O que é?

Sistema completo para **compra e venda de produtos informáticos** com:

✅ **Interface gráfica moderna** - Tkinter com abas (ttk.Notebook)  
✅ **Dois tipos de utilizadores** - Cliente (comprar) e Admin (gerir)  
✅ **Base de dados segura** - MySQL/MariaDB com bcrypt  
✅ **Carrinho de compras** - Adicionar/remover produtos  
✅ **Histórico de vendas** - Admin pode ver transações  
✅ **Validação de dados** - Email, telefone, passwords  

### Arquitetura

```
┌──────────────────────────────────────────────────────┐
│  APRESENTAÇÃO (Tkinter + ttk.Notebook)              │
│  ├─ Login                                            │
│  ├─ Interface Cliente (2 abas)                       │
│  └─ Interface Admin (3 abas)                         │
└──────────────────────────────────────────────────────┘
              ↕ (Controlador)
┌──────────────────────────────────────────────────────┐
│  LÓGICA (DatabaseManager)                           │
│  ├─ Autenticação                                     │
│  ├─ Operações CRUD                                   │
│  └─ Transações                                       │
└──────────────────────────────────────────────────────┘
              ↕ (Conexão)
┌──────────────────────────────────────────────────────┐
│  DADOS (MySQL/MariaDB)                              │
│  ├─ Tabelas (clientes, produtos, vendas, etc)       │
│  └─ Índices & Constraints                           │
└──────────────────────────────────────────────────────┘
```

---

## 🚀 Início Rápido

### Instalação (3 passos)

```bash
# 1. Clonar/descompactar projeto
cd /home/elgz/Documentos/Form_Prog_Python/Eng_Soft

# 2. Criar e ativar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 3. Instalar dependências e configurar BD
pip install -r requirements.txt
python3 setup_database_v2.py
```

### Executar

```bash
python3 sistema_loja_tkinter.py
```

---

## 👥 Utilizadores de Teste

### Clientes (Utilizadores Normais)

Todos têm password: `user123`

| Email | Nome | Tipo |
|-------|------|------|
| maria@example.com | Maria Silva | 👤 Cliente |
| pedro@example.com | Pedro Santos | 👤 Cliente |
| ana@example.com | Ana Costa | 👤 Cliente |
| carlos@example.com | Carlos Oliveira | 👤 Cliente |

### Administrador

| Email | Password | Tipo |
|-------|----------|------|
| admin@loja.com | admin123 | ▲ Admin |

---

## 🎯 Funcionalidades

### Para Clientes (👤)

**Aba 1: ▸ Explorar Produtos**
- Ver lista de todos os produtos
- Ver preço e quantidade em stock
- Adicionar produtos ao carrinho

**Aba 2: ▪ Carrinho**
- Ver itens no carrinho
- Alterar quantidades
- Remover produtos
- Ver total da compra
- **Checkout** (finalizar compra)

### Para Administradores (▲)

**Aba 1: ▬ Gerir Produtos**
- Ver todos os produtos
- Adicionar novo produto
- Editar produto existente
- Eliminar produto
- Ver quantidade em stock

**Aba 2: ◩ Gerir Clientes**
- Ver lista de clientes
- Ver detalhes do cliente
- Adicionar novo cliente
- Editar cliente
- Bloquear/desbloquear cliente

**Aba 3: ▣ Histórico de Vendas**
- Ver últimas 50 vendas
- Ver cliente, produtos, data e total
- Exportar relatório (futura feature)

---

## 📊 Base de Dados

### Tabelas Principais

```
clientes
  ├─ id_cliente (PK)
  ├─ nome
  ├─ email (UNIQUE)
  ├─ telefone
  ├─ senha_hash (bcrypt)
  └─ data_criacao

produtos
  ├─ id_produto (PK)
  ├─ nome
  ├─ descricao
  ├─ preco
  ├─ quantidade_stock
  └─ categoria

carrinho
  ├─ id_carrinho (PK)
  ├─ id_cliente (FK)
  ├─ id_produto (FK)
  ├─ quantidade
  └─ data_adicao

vendas
  ├─ id_venda (PK)
  ├─ id_cliente (FK)
  ├─ total
  ├─ data (TIMESTAMP)
  └─ status

venda_itens
  ├─ id_item (PK)
  ├─ id_venda (FK)
  ├─ id_produto (FK)
  ├─ quantidade
  └─ preco_unitario
```

### Índices de Performance

```sql
CREATE INDEX idx_cliente_email ON clientes(email);
CREATE INDEX idx_venda_cliente ON vendas(id_cliente);
CREATE INDEX idx_venda_data ON vendas(data);
CREATE INDEX idx_carrinho_cliente ON carrinho(id_cliente);
```

---

## 🔐 Segurança

### Passwords

- ✅ Criptografadas com **bcrypt** (12 rounds)
- ✅ Nunca armazenadas em texto plano
- ✅ Validação de força (recomendado: 8+ caracteres)

### SQL Injection

- ✅ **Prepared Statements** em todas as queries
- ✅ Nunca fazer concatenação de strings em SQL

### Validações

- ✅ Email válido (regex)
- ✅ Telefone mínimo 9 dígitos
- ✅ Password confirmar
- ✅ Input trimmed e sanitizado

---

## 📦 Dependências

```
mysql-connector-python==8.0.33  # Conexão BD
bcrypt==4.0.1                   # Criptografia
```

---

## 🛠️ Estructura de Arquivos

```
Eng_Soft/
├── sistema_loja_tkinter.py         # ⭐ Aplicação principal
├── setup_database_v2.py            # Criar/resetar BD
├── setup_complete.py               # Setup automático
├── requirements.txt                # Dependências
├── 00_LEIA-ME-PRIMEIRO.txt        # Entrada principal
├── ARQUITETURA.md                  # Documentação técnica
├── CONFIGURACAO.md                 # Setup & config
├── DESENVOLVIMENTO.md              # Guia extensão
├── GUIA_TKINTER.md                # Referência Tkinter
├── README_LOJA.md                 # Este arquivo
├── QUICK_START.md                 # Início rápido (EN)
├── test_loja.py                   # Testes unitários
├── test_validacoes.py             # Testes validações
└── venv/                           # Ambiente virtual
```

---

## 🧪 Testes

### Executar Testes

```bash
# Testes unitários
python3 test_loja.py

# Testes de validação
python3 test_validacoes.py
```

### Teste Manual

1. Executar `python3 sistema_loja_tkinter.py`
2. Login com `maria@example.com` / `user123`
3. Adicionar produtos ao carrinho
4. Ver carrinho
5. Finalizar compra
6. Logout

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'mysql'"

```bash
pip install mysql-connector-python
```

### "ModuleNotFoundError: No module named 'bcrypt'"

```bash
pip install bcrypt
```

### "Error connecting to database"

1. MariaDB/MySQL está em execução?
   ```bash
   sudo service mysql status
   ```

2. Credenciais corretas em `sistema_loja_tkinter.py`?

3. Base de dados existe?
   ```bash
   python3 setup_database_v2.py
   ```

### Tkinter não funciona (Linux)

```bash
sudo apt-get install python3-tk
```

---

## 📈 Melhorias Futuras

- [ ] Sistema de cupões de desconto
- [ ] Avaliações de produtos
- [ ] Wishlist/Favorites
- [ ] Notificações de stock baixo
- [ ] Relatórios em PDF
- [ ] API REST (para mobile app)
- [ ] Dark mode
- [ ] Suporte a múltiplas moedas
- [ ] Histórico de pedidos do cliente

---

## 🤝 Contribuição

Para estender o sistema:

1. Consultar [DESENVOLVIMENTO.md](DESENVOLVIMENTO.md) para exemplos
2. Revisar [ARQUITETURA.md](ARQUITETURA.md) para padrões
3. Seguir convenções de código existentes
4. Atualizar documentação

---

## 📝 Notas Importantes

### v1.0 → v2.0 (Mudanças Principais)

**Nova Interface com Abas:**
- ❌ Múltiplas janelas (Toplevel) → ✅ Abas únicas (ttk.Notebook)
- ❌ Emojis coloridos → ✅ Unicode símbolos profissionais
- ✅ Mesmo layout responsivo
- ✅ Mesma funcionalidade
- ✅ Melhor UX

**Banco de Dados:**
- ✅ Totalmente compatível com v1.0
- ✅ Sem perda de dados
- ✅ Pode-se reverter se necessário

---

## 📞 Suporte

- 📖 Documentação: Ver [00_LEIA-ME-PRIMEIRO.txt](00_LEIA-ME-PRIMEIRO.txt)
- 🏗️ Arquitetura: Ver [ARQUITETURA.md](ARQUITETURA.md)
- ⚙️ Configuração: Ver [CONFIGURACAO.md](CONFIGURACAO.md)
- 👨‍💻 Desenvolvimento: Ver [DESENVOLVIMENTO.md](DESENVOLVIMENTO.md)

---

**Desenvolvido em Python 3.8+**  
**Última Atualização:** 27 de fevereiro de 2026  
**Versão:** 2.0
