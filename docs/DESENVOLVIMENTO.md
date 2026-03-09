# 👨‍💻 GUIA DE DESENVOLVIMENTO - V2.0 Refatorado

Instruções para estender e modificar o sistema.

---

## 📚 Estrutura do Projeto Refatorado

```
loja_informatica/
├── src/
│   ├── config.py                    # Configurações centralizadas
│   ├── database.py                  # DatabaseManager
│   ├── models/                      # Modelos (Cliente, Produto)
│   ├── ui/                          # Interface gráfica (LojaApp)
│   │   ├── app.py
│   │   ├── screens/login.py
│   │   └── components/widgets.py
│   └── utils/                       # Utilitários
│       ├── security.py
│       └── validators.py
├── setup/database.py                # Setup da BD
├── main.py                          # Ponto de entrada
├── setup_db.py                      # Script de setup
└── requirements.txt
```

---

## 🔧 Entendendo a Arquitetura V2.0

### Padrão MVC (Model-View-Controller)

```
┌─────────────────────────────────────────────┐
│  APRESENTAÇÃO (View)                        │
│  ├─ exibir_login()                          │
│  ├─ criar_interface_cliente()  (com abas)   │
│  └─ criar_interface_admin()    (com abas)   │
└─────────────────────────────────────────────┘
              ↕
┌─────────────────────────────────────────────┐
│  LÓGICA (Controller)                        │
│  ├─ autenticar_cliente()                    │
│  ├─ adicionar_ao_carrinho()                 │
│  └─ processar_venda()                       │
└─────────────────────────────────────────────┘
              ↕
┌─────────────────────────────────────────────┐
│  DADOS (Model)                              │
│  └─ DatabaseManager                         │
│     ├─ executar_query()                     │
│     └─ executar_update()                    │
└─────────────────────────────────────────────┘
```

### Navegação com Abas (ttk.Notebook)

**Cliente - 2 Abas:**
```
┌────────────────────────────────────────────┐
│  ▸ Explorar  |  ▪ Carrinho                 │
├────────────────────────────────────────────┤
│                                            │
│   Conteúdo da aba selecionada              │
│                                            │
└────────────────────────────────────────────┘
```

**Admin - 3 Abas:**
```
┌────────────────────────────────────────────┐
│  ▬ Produtos  |  ◩ Clientes  |  ▣ Vendas   │
├────────────────────────────────────────────┤
│                                            │
│   Conteúdo da aba selecionada              │
│                                            │
└────────────────────────────────────────────┘
```

---

## 💡 Exemplo 1: Adicionar Campo em Clientes

### Cenário
Adicionar campo `data_nascimento` à tabela clientes.

### Passo 1: Migração da BD

Em `setup_database_v2.py`, adicione:

```python
# Nas migrações
ALTER_1 = """
ALTER TABLE clientes ADD COLUMN data_nascimento DATE AFTER email;
CREATE INDEX idx_cliente_nascimento ON clientes(data_nascimento);
"""
```

### Passo 2: Atualizar Interface

No método `_criar_aba_gerir_clientes()`:

```python
def _criar_aba_gerir_clientes(self):
    # ... código existente ...
    
    # NOVO: Campo de data
    ttk.Label(frame_form, text="Data Nascimento:").grid(row=3, column=0)
    entry_nascimento = ttk.Entry(frame_form)
    entry_nascimento.grid(row=3, column=1)
    
    # ... resto do código ...
```

### Passo 3: Validação

Adicione à classe `LojaApp`:

```python
def validar_data(self, data_str):
    """Valida formato AAAA-MM-DD"""
    try:
        from datetime import datetime
        datetime.strptime(data_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False
```

### Passo 4: Guardar Dados

No método de criar cliente:

```python
# ... existente ...
if not self.validar_data(entrada['data_nascimento']):
    messagebox.showerror("Erro", "Data inválida (AAAA-MM-DD)")
    return

# Inserir na BD
self.db.executar_update(
    "INSERT INTO clientes (nome, email, data_nascimento, telefone, senha_hash) "
    "VALUES (%s, %s, %s, %s, %s)",
    (nome, email, entrada['data_nascimento'], telefone, senha_hash)
)
```

---

## 🌟 Exemplo 2: Adicionar Sistema de Avaliações

### Passo 1: Criar Tabela

Em `setup_database_v2.py`:

```python
AVALIACOES_TABLE = """
CREATE TABLE avaliacoes (
    id_avaliacao INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT NOT NULL,
    id_produto INT NOT NULL,
    estrelas INT CHECK (estrelas BETWEEN 1 AND 5),
    comentario TEXT,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente) ON DELETE CASCADE,
    FOREIGN KEY (id_produto) REFERENCES produtos(id_produto) ON DELETE CASCADE,
    UNIQUE KEY unique_avaliacao (id_cliente, id_produto),
    INDEX idx_produto_media (id_produto)
);
"""
```

### Passo 2: Métodos na Classe DatabaseManager

```python
def adicionar_avaliacao(self, id_cliente, id_produto, estrelas, comentario):
    """Adiciona ou atualiza avaliação"""
    # Verificar se já avaliou
    resultado = self.executar_query(
        "SELECT id_avaliacao FROM avaliacoes "
        "WHERE id_cliente = %s AND id_produto = %s",
        (id_cliente, id_produto)
    )
    
    if resultado:
        # Atualizar
        self.executar_update(
            "UPDATE avaliacoes SET estrelas = %s, comentario = %s "
            "WHERE id_cliente = %s AND id_produto = %s",
            (estrelas, comentario, id_cliente, id_produto)
        )
    else:
        # Inserir
        self.executar_update(
            "INSERT INTO avaliacoes (id_cliente, id_produto, estrelas, comentario) "
            "VALUES (%s, %s, %s, %s)",
            (id_cliente, id_produto, estrelas, comentario)
        )

def obter_media_produto(self, id_produto):
    """Obtém média e contagem de avaliações"""
    resultado = self.executar_query(
        "SELECT AVG(estrelas) as media, COUNT(*) as total "
        "FROM avaliacoes WHERE id_produto = %s",
        (id_produto,)
    )
    
    if resultado and resultado[0]['media']:
        return float(resultado[0]['media']), resultado[0]['total']
    return 0, 0
```

### Passo 3: Interface - Adicionar Aba de Avaliações

Modificar `criar_interface_cliente()`:

```python
# Adicionar 3ª aba: Avaliações
aba_avaliacoes = ttk.Frame(notebook)
notebook.add(aba_avaliacoes, text="⭐ Avaliações")

# Listar produtos avaliados
frame_lista = ttk.Frame(aba_avaliacoes)
frame_lista.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

tree = ttk.Treeview(frame_lista, columns=('Produto', 'Estrelas', 'Data'), height=10)
tree.column('#0', width=0, stretch=tk.NO)
tree.column('Produto', anchor=tk.W, width=200)
tree.column('Estrelas', anchor=tk.CENTER, width=100)
tree.column('Data', anchor=tk.CENTER, width=100)

tree.heading('#0', text='', anchor=tk.W)
tree.heading('Produto', text='Produto')
tree.heading('Estrelas', text='★★★★★')
tree.heading('Data', text='Data')

# Preencher dados
avaliacoes = self.db.executar_query(
    "SELECT p.nome, a.estrelas, a.data_criacao FROM avaliacoes a "
    "JOIN produtos p ON a.id_produto = p.id_produto "
    "WHERE a.id_cliente = %s ORDER BY a.data_criacao DESC",
    (self.cliente_atual['id_cliente'],)
)

for av in avaliacoes:
    tree.insert('', tk.END, values=(av['nome'], '★' * av['estrelas'], av['data_criacao']))

tree.pack(fill=tk.BOTH, expand=True)
```

---

## 📦 Exemplo 3: Sistema de Cupões

### Passo 1: Tabela de Cupões

```python
CUPOES_TABLE = """
CREATE TABLE cupoes (
    id_cupao INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    desconto_percentual INT,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_expiracao DATE,
    ativo BOOLEAN DEFAULT TRUE,
    usos INT DEFAULT 0,
    usos_maximos INT,
    INDEX idx_codigo (codigo)
);
"""
```

### Passo 2: Validar Cupão

```python
def validar_cupao(self, codigo_cupao):
    """Valida e retorna desconto do cupão"""
    resultado = self.executar_query(
        "SELECT * FROM cupoes WHERE codigo = %s AND ativo = TRUE "
        "AND (data_expiracao IS NULL OR data_expiracao > NOW()) "
        "AND (usos_maximos IS NULL OR usos < usos_maximos)",
        (codigo_cupao.upper(),)
    )
    
    if resultado:
        return True, resultado[0]['desconto_percentual']
    return False, 0
```

### Passo 3: Aplicar Cupão no Carrinho

```python
# Na aba carrinho
frame_cupao = ttk.Frame(aba_carrinho)
frame_cupao.pack(pady=10)

ttk.Label(frame_cupao, text="Cupão:").pack(side=tk.LEFT, padx=5)
entry_cupao = ttk.Entry(frame_cupao, width=15)
entry_cupao.pack(side=tk.LEFT, padx=5)

def aplicar_cupao():
    cupao = entry_cupao.get().strip()
    valido, desconto = self.db.validar_cupao(cupao)
    
    if valido:
        self.desconto_cupao = desconto
        total = sum(item['preco'] * item['quantidade'] for item in self.carrinho)
        total_desconto = total * desconto / 100
        total_final = total - total_desconto
        label_total.config(text=f"Total: €{total_final:.2f} (desconto: {desconto}%)")
        messagebox.showinfo("Sucesso", f"✔ Cupão aplicado! Desconto: {desconto}%")
    else:
        messagebox.showerror("Erro", "✘ Cupão inválido ou expirado")

ttk.Button(frame_cupao, text="Aplicar", command=aplicar_cupao).pack(side=tk.LEFT, padx=5)
```

---

## 🔐 Exemplo 4: Validações de Segurança

### Email

```python
import re

def validar_email(self, email):
    """Valida formato de email"""
    padrão = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(padrão, email) is not None
```

### Telefone

```python
def validar_telefone(self, telefone):
    """Valida formato de telefone"""
    apenas_digitos = re.sub(r'\D', '', telefone)
    return len(apenas_digitos) >= 9
```

### Password

```python
def validar_password(self, password):
    """Valida força de password"""
    if len(password) < 8:
        return False, "Mínimo 8 caracteres"
    if not re.search(r'[A-Z]', password):
        return False, "Deve conter maiúsculas"
    if not re.search(r'[a-z]', password):
        return False, "Deve conter minúsculas"
    if not re.search(r'[0-9]', password):
        return False, "Deve conter números"
    return True, "OK"
```

---

## 🧪 Testando Extensões

### Teste Unitário Simples

```python
# test_extensoes.py
import unittest
from sistema_loja_tkinter import LojaApp

class TestAvaliacoes(unittest.TestCase):
    def setUp(self):
        self.app = LojaApp()
    
    def test_validar_cupao_valido(self):
        """Testa cupão válido"""
        valido, desconto = self.app.db.validar_cupao("DESCONTO10")
        self.assertTrue(valido)
        self.assertEqual(desconto, 10)
    
    def test_validar_cupao_invalido(self):
        """Testa cupão inválido"""
        valido, desconto = self.app.db.validar_cupao("INVALIDO000")
        self.assertFalse(valido)
        self.assertEqual(desconto, 0)

if __name__ == '__main__':
    unittest.main()
```

---

## 🐛 Debugging

### Modo Debug

Adicione no início de `sistema_loja_tkinter.py`:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('loja.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

Use ao longo do código:

```python
logger.debug(f"Carrinho atualizado: {self.carrinho}")
logger.info(f"Cliente {self.cliente_atual['nome']} fez login")
logger.error(f"Erro na BD: {erro}")
```

---

## 📋 Checklist para Novas Funcionalidades

- [ ] Criar tabela(s) na BD
- [ ] Adicionar método(s) a DatabaseManager
- [ ] Criar aba ou expandir aba existente na interface
- [ ] Adicionar validações
- [ ] Testar funcionalidade completa
- [ ] Atualizar documentação
- [ ] Fazer backup da BD
- [ ] Testar com dados reais

---

## 🚀 Performance & Otimizações

### Índices Recomendados

```sql
CREATE INDEX idx_cliente_email ON clientes(email);
CREATE INDEX idx_venda_cliente ON vendas(id_cliente);
CREATE INDEX idx_venda_data ON vendas(data);
CREATE INDEX idx_carrinho_cliente ON carrinho(id_cliente);
CREATE INDEX idx_avaliacao_produto ON avaliacoes(id_produto);
```

### Cache de Dados

```python
def __init__(self):
    # ...
    self.cache_produtos = {}
    self.cache_tempo = 0
    self.cache_intervalo = 300  # 5 minutos

def obter_produtos_cache(self):
    """Obtém produtos com cache"""
    import time
    agora = time.time()
    
    if self.cache_tempo + self.cache_intervalo < agora:
        self.cache_produtos = self.db.obter_todos_produtos()
        self.cache_tempo = agora
    
    return self.cache_produtos
```

---

## 🔄 Controle de Versão

### Migração de Dados Entre Versões

```python
# migration_v2_v3.py
def migrar_v2_para_v3(db):
    """Migração de v2.0 para v3.0"""
    
    # 1. Backup
    os.system("mysqldump -u root loja_informatica > backup_v2.sql")
    
    # 2. Alter tables
    db.executar_update("ALTER TABLE clientes ADD COLUMN telefono_alternativo VARCHAR(20)")
    
    # 3. Validação
    clientes = db.executar_query("SELECT COUNT(*) as total FROM clientes")
    print(f"✔ Migração completa! {clientes[0]['total']} clientes migrados")
```

---

## 📚 Recursos Úteis

- [Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)
- [MySQL/MariaDB Docs](https://mariadb.com/kb)
- [Python Regex](https://docs.python.org/3/library/re.html)
- [bcrypt](https://github.com/pyca/bcrypt)

---

**Última Atualização:** 27 de fevereiro de 2026  
**Versão:** 2.0
