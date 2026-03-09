# 📁 ESTRUTURA DO PROJETO - REFATORADO

## Visão Geral da Estrutura

O projeto foi refatorado para seguir a arquitetura MVC encapsulada em módulos bem organizados.

```
loja_informatica/
├── src/                              # ★ CÓDIGO FONTE PRINCIPAL
│   ├── __init__.py
│   ├── config.py                     # Configurações centralizadas
│   ├── database.py                   # Gerenciador de BD (DatabaseManager)
│   │
│   ├── models/                       # Modelos de dados
│   │   ├── __init__.py
│   │   ├── cliente.py                # Classe Cliente
│   │   └── produto.py                # Classe Produto
│   │
│   ├── ui/                           # Interface Gráfica (Vista)
│   │   ├── __init__.py
│   │   ├── app.py                    # LojaApp - Aplicação principal
│   │   │
│   │   ├── screens/                  # Telas da aplicação
│   │   │   ├── __init__.py
│   │   │   └── login.py              # Tela de login
│   │   │
│   │   └── components/               # Componentes reutilizáveis
│   │       ├── __init__.py
│   │       └── widgets.py            # Widgets customizados (logo, etc)
│   │
│   └── utils/                        # Utilidades
│       ├── __init__.py
│       ├── security.py               # Hash/verificação de passwords (bcrypt)
│       └── validators.py             # Validadores de dados (email, preço, etc)
│
├── setup/                            # ★ CONFIGURAÇÃO INICIAL
│   ├── __init__.py
│   └── database.py                   # Script de setup da BD
│
├── main.py                           # ★ PONTO DE ENTRADA (executar aplicação)
├── setup_db.py                       # ★ SCRIPT PARA CONFIGURAR BD
├── requirements.txt                  # Dependências Python
├── README.md                         # Documentação principal
├── ESTRUTURA.md                      # Este ficheiro
└── venv/                             # Ambiente virtual (não versionar)
```

---

## 📋 Descrição dos Ficheiros Principais

### Numa Linha Rápida

| Ficheiro | Propósito |
|----------|-----------|
| `main.py` | **Executar a aplicação** |
| `setup_db.py` | **Configurar base de dados** |
| `src/config.py` | Constantes e configurações |
| `src/database.py` | Conexão e queries BD |
| `src/ui/app.py` | Interface gráfica (LojaApp) |
| `src/utils/security.py` | Encriptação de passwords |
| `src/utils/validators.py` | Validação de dados |
| `setup/database.py` | Setup BD (tabelas, índices, dados) |

---

## 🎯 Como Usar Cada Ficheiro

### 1. EXECUTAR APLICAÇÃO
```bash
python main.py
```
→ Lança a GUI da aplicação

### 2. SETUP BASE DE DADOS
```bash
python setup_db.py
```
→ Cria BD, tabelas e utilizadores de teste

### 3. MODIFICAR CONFIGURAÇÕES
Editar `src/config.py`:
- Credenciais BD
- Dimensões da janela
- Fontes e cores
- Padrões de validação

---

## 🏗️ Arquitetura Modular

### Camadas

```
┌─────────────────────────────────────┐
│  Apresentação (UI)                  │
│  / src/ui/app.py                    │
│  / src/ui/screens/                  │
│  \ src/ui/components/               │
├─────────────────────────────────────┤
│  Lógica de Negócio                  │
│  / src/utils/validators.py          │
│  / src/models/                      │
├─────────────────────────────────────┤
│  Dados (BD)                         │
│  / src/database.py                  │
│  / setup/database.py                │
└─────────────────────────────────────┘
```

### Fluxo de Dados

```
UI (Tkinter)
    ↓
LojaApp.py (Controlador)
    ↓
DatabaseManager (Módulo database.py)
    ↓
MariaDB/MySQL
```

---

## 🔧 Configuração Rápida

### Alterar credenciais BD
```python
# src/config.py
DATABASE_CONFIG = {
    'host': 'seu_host',
    'user': 'seu_user',
    'password': 'sua_senha',
    'database': 'loja_informatica'
}
```

### Alterar tema/cores
```python
# src/config.py
COLORS = {
    'bg': '#f0f0f0',
    'logo_bg': '#E0CF34',
    'logo_text': '#165fa3',
}
```

---

## 📦 Dependências

Instaladas via `pip install -r requirements.txt`:
- `mysql-connector-python` - Conexão com BD
- `bcrypt` - Hash seguro de passwords

Tkinter vem nativo no Python (não precisa instalar).

---

## ✅ Benefícios da Refatoração

✔ **Modularização** - Cada módulo tem responsabilidade clara  
✔ **Reutilização** - Código não duplicado  
✔ **Manutenibilidade** - Fácil encontrar e modificar código  
✔ **Escalabilidade** - Pronto para novos recursos  
✔ **Testes** - Cada módulo pode ser testado isoladamente  
✔ **Documentação** - Código autodocumentado  

---

## 🗑️ Ficheiros Eliminados (Refatoração)

❌ `sistema_loja_tkinter.py` → Refatorado em `src/ui/app.py`  
❌ `system_loja_informatica.py` → Versão antiga removida  
❌ `setup_database_v2.py` → Integrado em `setup/database.py`  
❌ `setup_completo.py` → Substituído por `setup_db.py`  
❌ `test_*.py` → Ficheiros de teste removidos  
❌ `inserir_clientes_teste.py` → Integrado no setup  
❌ Documentação redundante (QUICK_START, RESUMO, etc)  

---

## 🚀 Próximos Passos

1. **Análise do Código**
   ```bash
   # Ver estrutura real
   tree /F src/
   ```

2. **Executar Setup**
   ```bash
   python setup_db.py
   ```

3. **Iniciar Aplicação**
   ```bash
   python main.py
   ```

4. **Estender Funcionalidades**
   - Adicionar novos modelos em `src/models/`
   - Novos validadores em `src/utils/validators.py`
   - Novas telas em `src/ui/screens/`

---

**Projeto refatorado com abordagem profissional e escalável** ✨
