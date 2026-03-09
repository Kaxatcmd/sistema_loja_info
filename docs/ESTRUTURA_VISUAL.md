```
📦 loja_informatica/
│
├── 📄 main.py                          # ★ EXECUTAR AQUI (python main.py)
├── 📄 setup_db.py                      # ★ SETUP: (python setup_db.py)
│
├── 📁 src/                             # Código fonte principal
│   ├── __init__.py
│   ├── 📄 config.py                    # ⚙️ Configurações centralizadas
│   ├── 📄 database.py                  # 🗄️ DatabaseManager
│   │
│   ├── 📁 models/                      # 📊 Modelos de dados
│   │   ├── __init__.py
│   │   ├── cliente.py                  # Classe Cliente
│   │   └── produto.py                  # Classe Produto
│   │
│   ├── 📁 ui/                          # 🎨 Interface Gráfica
│   │   ├── __init__.py
│   │   ├── 📄 app.py                   # ⭐ LojaApp (Principal)
│   │   │
│   │   ├── 📁 screens/                 # Telas
│   │   │   ├── __init__.py
│   │   │   └── login.py                # 🔐 Tela de Login
│   │   │
│   │   └── 📁 components/              # Componentes reutilizáveis
│   │       ├── __init__.py
│   │       └── widgets.py              # 🎯 Logo, widgets
│   │
│   └── 📁 utils/                       # 🔧 Utilitários
│       ├── __init__.py
│       ├── 📄 security.py              # 🔒 Hash/verificação passwords
│       └── 📄 validators.py            # ✅ Validação de dados
│
├── 📁 setup/                           # 🗄️ Setup da BD
│   ├── __init__.py
│   └── 📄 database.py                  # Script de inicialização
│
├── 📁 venv/                            # Virtual environment (venv não versionar)
│   └── ...
│
├── 📄 requirements.txt                 # 📋 Dependências Python
│
├── 📄 README.md                        # 📘 Documentação principal
├── 📄 ESTRUTURA.md                     # 📍 Organização do projeto
├── 📄 INICIO_RAPIDO.md                 # 🚀 Começar em 3 passos
├── 📄 GUIA_EXTENSAO.md                 # 🔧 Como estender
├── 📄 RESUMO_REFATORACAO.md            # ✨ Detalhes da refatoração
│
├── 📄 ARQUITETURA.md                   # 🏗️ Design técnico (existente)
├── 📄 DESENVOLVIMENTO.md               # 👨‍💻 Guia devs (existente)
├── 📄 CONFIGURACAO.md                  # ⚙️ Configuração (existente)
├── 📄 DETALHES_TECNICOS.md             # 🔬 Detalhes (existente)
├── 📄 GUIA_TKINTER.md                  # 🎨 Tkinter (existente)
└── 📄 PONTOS_DE_INTERESSE.md           # 📌 Pontos relevantes (existente)
```

---

## 🎯 Ficheiros Principais

### Para Executar ▶️
```bash
python main.py           # Inicia a aplicação
python setup_db.py       # Configura base de dados
```

### Para Entender 📚
```
INICIO_RAPIDO.md         # Começar rápido (3 passos)
ESTRUTURA.md             # Layout do projeto
README.md                # Documentação completa
RESUMO_REFATORACAO.md    # O que foi refatorado
```

### Para Desenvolver 💻
```
GUIA_EXTENSAO.md         # Como adicionar features
src/config.py            # Alterar configurações
src/utils/validators.py  # Adicionar validadores
src/ui/screens/          # Adicionar novas telas
src/models/              # Adicionar novos modelos
```

---

## 📊 Estrutura em Níveis

### Nível 0: Entrada
```
main.py → src/ui/app.py (LojaApp)
```

### Nível 1: Autenticação
```
src/ui/screens/login.py → src/utils/security.py
```

### Nível 2: Interface
```
src/ui/app.py (LojaApp)
├── src/ui/screens/
├── src/ui/components/
└── src/config.py (Estilos)
```

### Nível 3: Lógica
```
src/utils/validators.py  # Validar dados
src/utils/security.py    # Hash passwords
src/models/              # Estrutura dados
```

### Nível 4: Dados
```
src/database.py (DatabaseManager)
└── setup/database.py (Setup BD)
```

---

## 🔄 Fluxo de Dados

```
Usuario
   ↓
main.py
   ↓
LojaApp (src/ui/app.py)
   ├→ LoginScreen (src/ui/screens/login.py)
   │   └→ DatabaseManager (src/database.py)
   │
   ├→ InterfaceCliente
   │   ├→ Validators (src/utils/validators.py)
   │   ├→ Components (src/ui/components/)
   │   └→ DatabaseManager
   │
   └→ InterfaceAdmin
       ├→ Validators
       ├→ Components
       └→ DatabaseManager
```

---

## ⚡ Quick Reference

| Ação | Ficheiro |
|------|----------|
| Executar | main.py |
| Setup BD | setup_db.py |
| Mudar cores/fonts | src/config.py |
| Adicionar validador | src/utils/validators.py |
| Adicionar encriptação | src/utils/security.py |
| Adicionar modelo | src/models/ + setup/database.py |
| Adicionar tela | src/ui/screens/ + src/ui/app.py |
| Adicionar componente | src/ui/components/widgets.py |

---

**Estrutura pronta para produção!** ✅
