# 📐 ARQUITETURA DO SISTEMA - V2.0

## Visão Geral

O **Sistema de Loja de Informática** é uma aplicação desktop Python com interface gráfica baseada em Tkinter e armazenamento de dados em MariaDB/MySQL.

**Versão:** 2.0  
**Data:** 27 de fevereiro de 2026  
**Arquitetura:** Cliente-Servidor (Desktop + BD Remota)

---

## 🏗️ Componentes Principais

### 1. Camada de Apresentação (GUI)
- **Framework:** Tkinter (nativo do Python)
- **Componente:** `ttk.Notebook` (Abas)
- **Arquivo:** `sistema_loja_tkinter.py`
- **Características:**
  - Interface com **abas** em vez de múltiplas janelas
  - Responsivo e profissional
  - Ícones Unicode minimalistas
  - Sem dependências externas para GUI

### 2. Camada de Negócio (Lógica)
- **Classe:** `LojaApp` (controlador principal)
- **Responsabilidades:**
  - Gerenciar estado da aplicação
  - Controlar fluxo de navegação entre abas
  - Validar entradas do utilizador
  - Orquestrar operações de negócio

### 3. Camada de Dados (DB)
- **SGBD:** MariaDB/MySQL
- **Classe:** `DatabaseManager`
- **Responsabilidades:**
  - Gerir conexões com BD
  - Executar queries SELECT
  - Executar operações INSERT/UPDATE/DELETE
  - Tratamento de erros de BD

---

## 📊 Estrutura da Base de Dados

### Tabelas Principais

```sql
clientes
├── id_cliente (PK)
├── nome
├── email (UNIQUE)
├── telefone
├── password (hash bcrypt)
├── is_admin (boolean)
└── data_criacao

produtos
├── id_produto (PK)
├── nome
├── descricao
├── preco
├── stock
└── data_criacao

vendas
├── id_venda (PK)
├── id_cliente (FK)
├── data
├── total
└── data_criacao

venda_produto (tabela de junção)
├── id_venda_produto (PK)
├── id_venda (FK)
├── id_produto (FK)
├── preco
├── quantidade
└── data_criacao
```

---

## 🔄 Fluxo de Dados

### 1. Autenticação
```
Utilizador preenche email/password
     ↓
Form de Login
     ↓
DatabaseManager.executar_query()
     ↓
Validação com bcrypt
     ↓
Carrego interface (Cliente ou Admin)
```

### 2. Fluxo de Cliente

#### Aba 1: Explorar Produtos
```
Aba "Explorar Produtos" aberta
     ↓
Query: SELECT * FROM produtos WHERE stock > 0
     ↓
Listbox preenchido
     ↓
Utilizador seleciona + clica "Adicionar"
     ↓
Produto adicionado a self.carrinho (memória)
     ↓
Mensagem de confirmação
     ↓
Aba "Ver Carrinho" atualizada automaticamente
```

#### Aba 2: Ver Carrinho
```
Aba "Ver Carrinho" aberta
     ↓
Exibir items do carrinho (self.carrinho)
     ↓
Calcular total
     ↓
Utilizador clica "Finalizar Compra"
     ↓
INSERT venda + INSERT venda_produto
     ↓
UPDATE produtos SET stock = stock - 1
     ↓
Carrinho limpo
     ↓
Voltano à aba produtos
```

### 3. Fluxo de Administrador

#### Aba 1: Gerir Produtos
```
Aba "Gerir Produtos" aberta
     ↓
Query: SELECT * FROM produtos
     ↓
Text widget exibe tabela
     ↓
Botão "Recarregar" para atualizar
```

#### Aba 2: Gerir Clientes
```
Aba "Gerir Clientes" aberta
     ↓
Query: SELECT * FROM clientes
     ↓
Text widget exibe tabela
     ↓
Mostra status de admin (▲ ou ◦)
```

#### Aba 3: Ver Vendas
```
Aba "Ver Vendas" aberta
     ↓
Query: SELECT vendas JOIN clientes (últimas 50)
     ↓
Text widget exibe histórico
     ↓
Mostra ID, Cliente, Data, Total
```

---

## 🎭 Padrões de Design Utilizados

### 1. **MVC (Model-View-Controller)**
- **Model:** `DatabaseManager` (acesso a dados)
- **View:** Widgets Tkinter (abas, labels, buttons)
- **Controller:** `LojaApp` (lógica de negócio)

### 2. **Singleton Pattern**
- Uma única instância de `DatabaseManager` por aplicação
- Uma única connexão à BD (reutilizada)

### 3. **Strategy Pattern**
- Interfaces diferentes para clientes vs admins
- Métodos especializados por tipo de utilizador

### 4. **Observer Pattern**
- Atualização automática de abas (ex: carrinho)
- Refresh de dados ao trocar de aba

---

## 🔐 Segurança

### Autenticação
- **Método:** Email + Password com hash bcrypt
- **Hash:** bcrypt com 12 rounds
- **Verificação:** `bcrypt.checkpw()`

### Proteção contra SQL Injection
- **Método:** Prepared statements
- **Implementação:** Parâmetros `%s` em queries
- **Exemplo:**
  ```python
  cursor.execute("SELECT * FROM clientes WHERE email = %s", (email,))
  ```

### Autorização
- **Método:** Verificação de `is_admin` no login
- **Resultado:** Interface diferente por tipo de utilizador

---

## 📈 Escalabilidade

### Limitações Atuais
- Interface desktop (não web)
- Uma conexão por aplicação
- Limite de ~50 registos por aba

### Propostas de Melhoria
- [ ] Conexão em pool para múltiplas conexões
- [ ] Paginação de dados para grandes conjuntos
- [ ] Cache de consultas frequentes
- [ ] Versão web com Django/Flask

---

## 🔄 Ciclo de Vida da Aplicação

```
1. Inicialização
   ├── Carregar configurações
   ├── Conectar à BD
   └── Exibir login

2. Autenticação
   ├── Validar credenciais
   ├── Determinar tipo de utilizador
   └── Carregar interface apropriada

3. Interação
   ├── Utilizador navega entre abas
   ├── Eventos gatilham queries
   ├── Dados são persistidos
   └── UI atualiza-se

4. Logout
   ├── Limpar memória (carrinho, utilizador)
   ├── Voltar ao login
   └── Aguardar próximo utilizador

5. Encerramento
   ├── Desconectar da BD
   └── Fechar aplicação
```

---

## 💾 Armazenamento de Estado

### Estado em Memória
```python
self.usuario_atual     # Dict com dados do cliente
self.carrinho          # Lista de produtos selecionados
self.notebook          # Referência para abas
```

### Persistência em BD
```
- Produtos: sempre salvos
- Clientes: sempre salvos
- Vendas: salvos ao finalizar compra
- Carrinho: não persistente (apenas na sessão)
```

---

## 🎯 Mapeamento de Abas

### Cliente Normal
| Nome da Aba | Variable | Função |
|-------------|----------|--------|
| ▸ Explorar Produtos | `frame_produtos` | `_criar_aba_explorar_produtos()` |
| ▪ Ver Carrinho | `frame_carrinho` | `_criar_aba_carrinho()` |

### Administrador
| Nome da Aba | Variable | Função |
|-------------|----------|--------|
| ▬ Gerir Produtos | `frame_produtos` | `_criar_aba_gerir_produtos()` |
| ◩ Gerir Clientes | `frame_clientes` | `_criar_aba_gerir_clientes()` |
| ▣ Ver Vendas | `frame_vendas` | `_criar_aba_vendas()` |

---

## 🚀 Fluxo de Inicialização

```python
main()
  ↓
root = tk.Tk()
  ↓
app = LojaApp(root)
  ├── DatabaseManager.conectar()
  └── exibir_login()
  ↓
root.mainloop()
```

---

## 📝 Convenções de Código

### Nomes de Variáveis
- `frame_*` - Frames Tkinter
- `text_*` - Text widgets
- `listbox_*` - Listbox widgets
- `self.usuario_atual` - Dados do utilizador autenticado
- `self.carrinho` - Lista de itens do carrinho

### Nomes de Funções
- `criar_interface_*()` - Criar interfaces completas
- `_criar_aba_*()` - Criar uma aba (privado)
- `fazer_*()` - Ações do utilizador
- `_atualizar_*()` - Atualizar parte da UI (privado)

### Documentação
```python
def minha_funcao(param1):
    """Descrição breve
    
    Descrição detalhada se necessário
    """
```

---

## 🔗 Dependências Externas

```
mysql-connector-python  → Conexão com MariaDB
bcrypt                  → Hash de passwords
Tkinter                 → GUI (incluído no Python)
```

---

## 📚 Referências

- Documentação Tkinter: https://docs.python.org/3/library/tkinter.html
- ttk.Notebook: https://tkdocs.com/tutorial/index.html
- MySQL Connector: https://dev.mysql.com/doc/connector-python/en/
- Bcrypt: https://github.com/pyca/bcrypt
