# 📱 Sistema de Loja de Informática - Versão 2.0 Refatorada

## Visão Geral

Aplicação desktop completa para compra e venda de produtos informáticos, desenvolvida com **Python 3.8+**, **Tkinter** e **MariaDB/MySQL**.

**Versão:** 2.0 Refatorada  
**Data:** 2026  
**Status:** ✔ Estrutura Modularizada  

---

## 🎯 Objetivos

✅ Gestão de produtos informáticos  
✅ Carrinho de compras funcional  
✅ Histórico de transações  
✅ Interface dupla (Cliente/Administrador)  
✅ Autenticação com bcrypt  
✅ Estrutura modular e escalável  

---

## 📁 Estrutura do Projeto

```
loja_informatica/
├── src/                           # Código fonte principal
│   ├── __init__.py
│   ├── config.py                  # Configurações da aplicação
│   ├── database.py                # Gerenciador de BD
│   ├── models/                    # Modelos de dados
│   │   ├── cliente.py
│   │   └── produto.py
│   ├── ui/                        # Interface gráfica
│   │   ├── app.py                 # Aplicação principal (LojaApp)
│   │   ├── screens/
│   │   │   └── login.py           # Tela de login
│   │   └── components/
│   │       └── widgets.py         # Componentes reutilizáveis
│   └── utils/                     # Utilitários
│       ├── security.py            # Hash e verificação de passwords
│       └── validators.py          # Validadores de dados
├── setup/                         # Configuração inicial
│   └── database.py                # Script de setup de BD
├── main.py                        # Ponto de entrada principal
├── setup_db.py                    # Script para inicializar BD
├── requirements.txt               # Dependências Python
└── README.md                      # Documentação
```

---

## 🚀 Início Rápido

### 1. Preparar Ambiente

```bash
# Criar ambiente virtual (Linux/Mac)
python3 -m venv venv
source venv/bin/activate

# Criar ambiente virtual (Windows)
python -m venv venv
venv\Scripts\activate
```

### 2. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar Base de Dados

```bash
python setup_db.py
```

Isso irá:
- Criar base de dados `loja_informatica`
- Criar todas as tabelas necessárias
- Inserir utilizadores de teste

### 4. Executar Aplicação

```bash
python main.py
```

---

## 🔐 Credenciais de Teste

**Administrador:**
- Email: `admin@example.com`
- Password: `admin123`

**Cliente:**
- Email: `cliente@example.com`
- Password: `user123`

---

## 📊 Arquitetura

### Padrão MVC

```
Model (BD)  ←→  Controller (Lógica)  ←→  View (GUI)
    ↓                  ↓                    ↓
database.py      utils/, models/      ui/app.py
```

### Componentes Principais

| Módulo | Responsabilidade |
|--------|-----------------|
| `src/database.py` | Operações com BD |
| `src/ui/app.py` | Interface gráfica principal |
| `src/utils/security.py` | Criptografia de passwords |
| `src/utils/validators.py` | Validação de dados |
| `setup/database.py` | Inicialização de BD |

---

## 📦 Dependencies

- **Python:** 3.8+
- **MySQL Connector:** Para conexão com BD
- **bcrypt:** Para hash seguro de passwords
- **Tkinter:** GUI (incluso no Python)

---

## 🎓 Princípios de Design

### Separação de Responsabilidades
- **Modelos** (.models): Estrutura de dados
- **Banco de Dados** (database.py): Acesso a dados
- **Interface** (ui/): Apresentação
- **Utilidades** (utils/): Funções auxiliares

### Reutilização de Código
- Componentes UI em `ui/components/`
- Validadores centralizados em `utils/validators.py`
- Segurança em `utils/security.py`

### Configuração Centralizada
- Todas as constantes em `src/config.py`
- Fácil manutenção e colaboração

---

## 🔧 Configuração

Editar `src/config.py` para:
- Alterar host/credenciais da BD
- Ajustar dimensões da janela
- Modificar fontes e cores

---

## 📝 Features Implementadas

### Cliente
- ✅ Login/Logout seguro
- ✅ Ver produtos disponíveis
- ✅ Adicionar ao carrinho
- ✅ Finalizar compra
- ✅ Ver histórico pessoal

### Administrador
- ✅ Gerir produtos (adicionar, editar, listar)
- ✅ Gerir clientes
- ✅ Ver histórico de vendas
- ✅ Estatísticas de vendas

---

## 🚀 Próximas Melhorias (V3.0)

- [ ] Sistema de cupões
- [ ] Avaliações de produtos
- [ ] Wishlist/Favoritos
- [ ] Notificações de stock
- [ ] Relatórios em PDF
- [ ] API REST
- [ ] Dark mode
- [ ] Múltiplas moedas

---

## 📧 Suporte

Para questões ou bugs, criar issue no repositório.

---

**Desenvolvido com ❤️ em Python**
