# 📑 ÍNDICE DO PROJETO

Guia completo de documentação e arquivos do projeto.

---

## 🎯 Começo Rápido

👉 **Novo? Comece aqui:**

1. [00_LEIA-ME-PRIMEIRO.txt](00_LEIA-ME-PRIMEIRO.txt) - Orientação básica
2. [QUICK_START_PT.md](QUICK_START_PT.md) - Início em 3 passos (PT)
3. [QUICK_START.md](QUICK_START.md) - Início em 3 passos (EN)

---

## 📚 Documentação por Tema

### 🏫 Para Iniciantes

| Documento | Conteúdo |
|-----------|----------|
| [00_LEIA-ME-PRIMEIRO.txt](00_LEIA-ME-PRIMEIRO.txt) | Entrada principal, orientação |
| [QUICK_START_PT.md](QUICK_START_PT.md) | Instalação rápida (português) |
| [QUICK_START.md](QUICK_START.md) | Instalação rápida (inglês) |
| [README_LOJA.md](README_LOJA.md) | Visão geral do projeto |

### 🏗️ Para Arquitetos

| Documento | Conteúdo |
|-----------|----------|
| [ARQUITETURA.md](ARQUITETURA.md) | Padrões MVC, componentes, dados |
| [RESUMO_PROJETO.md](RESUMO_PROJETO.md) | Status, features, roadmap |
| [DETALHES_TECNICOS.md](DETALHES_TECNICOS.md) | Specs técnicas, performance |

### ⚙️ Para Desenvolvedores

| Documento | Conteúdo |
|-----------|----------|
| [DESENVOLVIMENTO.md](DESENVOLVIMENTO.md) | Como estender, exemplos |
| [CONFIGURACAO.md](CONFIGURACAO.md) | Setup, customização, deployment |
| [GUIA_TKINTER.md](GUIA_TKINTER.md) | Referência de widgets e padrões |

### 📋 Referência

| Documento | Conteúdo |
|-----------|----------|
| [RESUMO_TKINTER.txt](RESUMO_TKINTER.txt) | Status v2.0, tecnologias |
| [ICONES_UNICODE.md](ICONES_UNICODE.md) | Sistema de ícones |
| [ICONES_REFERENCIA.md](ICONES_REFERENCIA.md) | Tabela de ícones Unicode |

---

## 💻 Arquivos de Código

### Arquivos Principais

| Arquivo | Linhas | Descrição |
|---------|--------|-----------|
| [sistema_loja_tkinter.py](sistema_loja_tkinter.py) | 450+ | ⭐ Aplicação GUI principal |
| [setup_database_v2.py](setup_database_v2.py) | 300+ | Base de dados inicial |
| [DatabaseManager](sistema_loja_tkinter.py#L1) | 200+ | Gerenciador de BD (classe) |

### Testes

| Arquivo | Descrição |
|---------|-----------|
| [test_loja.py](test_loja.py) | Testes unitários gerais |
| [test_validacoes.py](test_validacoes.py) | Testes de validação |

### Legacy (Versão Anterior)

| Arquivo | Nota |
|---------|------|
| sistema_loja_tkinter_OLD.py | Backup v1.0 (antes de refactor para abas) |
| system_loja_informatica.py | PySimpleGUI (obsoleto) |
| setup_database.py | BD setup v1.0 (obsoleto) |
| admin_loja.py | Admin antigo (obsoleto) |

### Utilitários

| Arquivo | Descrição |
|---------|-----------|
| requirements.txt | Dependências Python |
| run.sh | Script de execução |
| resumo_status.sh | Status do projeto |

---

## 📖 Documentação Detalhada

### 🎨 Interface & UX

**Arquivo:** [00_LEIA-ME-PRIMEIRO.txt](00_LEIA-ME-PRIMEIRO.txt)

```
▸ Visão geral do sistema
▸ Como usar (cliente e admin)
▸ Estrutura de abas
▸ Exemplo prático passo-a-passo
▸ FAQ  
▸ Troubleshooting
```

**Arquivo:** [GUIA_TKINTER.md](GUIA_TKINTER.md)

```
▸ Widgets Tkinter (Label, Button, Entry, etc)
▸ ttk.Notebook (abas)
▸ Layouts (pack, grid, place)
▸ Temas e cores
▸ Validação de input
▸ Exemplos de código
```

### 🏗️ Arquitectura

**Arquivo:** [ARQUITETURA.md](ARQUITETURA.md)

```
▸ Padrão MVC
▸ Estrutura de componentes
▸ Base de dados (tabelas, índices)
▸ Fluxo de dados
▸ Design patterns usados
▸ Segurança
▸ Performance
```

**Arquivo:** [DETALHES_TECNICOS.md](DETALHES_TECNICOS.md)

```
▸ Stack técnico
▸ Dependências
▸ Configuração de ambiente
▸ Performance & otimizações
▸ Índices recomendados
```

### 🚀 Instalação & Setup

**Arquivo:** [CONFIGURACAO.md](CONFIGURACAO.md)

```
▸ Instalação passo-a-passo
▸ Configuração de BD
▸ Credenciais e segurança
▸ Servidor remoto
▸ Variáveis de ambiente
▸ Backup & restore
▸ Troubleshooting
```

**Arquivo:** [RESUMO_TKINTER.txt](RESUMO_TKINTER.txt)

```
▸ Status v2.0
▸ Mudanças principais
▸ Features implementadas
▸ Arquivos principais
▸ Utilizadores de teste
▸ Como começar
```

### 👨‍💻 Desenvolvimento

**Arquivo:** [DESENVOLVIMENTO.md](DESENVOLVIMENTO.md)

```
▸ 4 exemplos práticos:
  1. Adicionar campo em clientes
  2. Sistema de avaliações
  3. Cupões de desconto
  4. Validações de segurança
▸ Testes unitários
▸ Debugging
▸ Deployment
```

---

## 🎯 Por Objetivo

### Quero Começar Rapidamente

1. [QUICK_START_PT.md](QUICK_START_PT.md) - 5 minutos
2. [00_LEIA-ME-PRIMEIRO.txt](00_LEIA-ME-PRIMEIRO.txt) - 15 minutos

### Quero Entender a Arquitetura

1. [README_LOJA.md](README_LOJA.md) - Visão geral
2. [ARQUITETURA.md](ARQUITETURA.md) - Detalhes técnicos
3. [DETALHES_TECNICOS.md](DETALHES_TECNICOS.md) - Specs

### Quero Estender o Sistema

1. [DESENVOLVIMENTO.md](DESENVOLVIMENTO.md) - Exemplos
2. [GUIA_TKINTER.md](GUIA_TKINTER.md) - Referência widgets
3. [CONFIGURACAO.md](CONFIGURACAO.md) - Setup avançado

### Quero Fazer Deploy

1. [CONFIGURACAO.md](CONFIGURACAO.md) - Setup
2. [DETALHES_TECNICOS.md](DETALHES_TECNICOS.md) - Performance
3. [ARQUITETURA.md](ARQUITETURA.md) - Padrões

### Estou com Problemas

1. [00_LEIA-ME-PRIMEIRO.txt](00_LEIA-ME-PRIMEIRO.txt) - FAQ
2. [CONFIGURACAO.md](CONFIGURACAO.md) - Troubleshooting
3. [DETALHES_TECNICOS.md](DETALHES_TECNICOS.md) - Issues conhecidos

---

## 📊 Hierarquia de Documentos

```
00_LEIA-ME-PRIMEIRO.txt
├── QUICK_START_PT.md ........... Para começar em PT
├── QUICK_START.md ............. Para começar em EN
├── README_LOJA.md ............. Visão geral
│
├── ARQUITETURA.md .................. Arquitetura MVC
│   ├── DETALHES_TECNICOS.md ....... Specs técnicas
│   └── DESENVOLVIMENTO.md ......... Exemplos práticos
│
├── CONFIGURACAO.md ......... Setup & customização
│   ├── GUIA_TKINTER.md ..... Referência widgets
│   └── DESENVOLVIMENTO.md .. Extensões
│
└── Referência
    ├── RESUMO_TKINTER.txt ...... Status v2.0
    ├── RESUMO_PROJETO.md ....... Features & roadmap
    ├── ICONES_UNICODE.md ....... Sistema de ícones
    └── ICONES_REFERENCIA.md .... Tabela de caracteres
```

---

## 🔍 Busca Rápida por Palavra-Chave

### Installação
- [QUICK_START_PT.md](QUICK_START_PT.md#instalação)
- [CONFIGURACAO.md](CONFIGURACAO.md#instalação-passo-a-passo)

### Base de Dados
- [ARQUITETURA.md](ARQUITETURA.md#base-de-dados)
- [DETALHES_TECNICOS.md](DETALHES_TECNICOS.md#banco-de-dados)
- [DESENVOLVIMENTO.md](DESENVOLVIMENTO.md#banco-de-dados)

### Segurança
- [ARQUITETURA.md](ARQUITETURA.md#segurança)
- [CONFIGURACAO.md](CONFIGURACAO.md#configuração-de-segurança)
- [DESENVOLVIMENTO.md](DESENVOLVIMENTO.md#validações-de-segurança)

### Performance
- [DETALHES_TECNICOS.md](DETALHES_TECNICOS.md#performance)
- [DESENVOLVIMENTO.md](DESENVOLVIMENTO.md#performance)

### Widgets Tkinter
- [GUIA_TKINTER.md](GUIA_TKINTER.md)
- [DESENVOLVIMENTO.md](DESENVOLVIMENTO.md#interface-widget)

### Ícones Unicode
- [ICONES_UNICODE.md](ICONES_UNICODE.md)
- [ICONES_REFERENCIA.md](ICONES_REFERENCIA.md)

---

## 📶 Versão & Status

| Aspecto | Status |
|---------|--------|
| Versão Atual | 2.0 (Estável) |
| Data Atualização | 27 de fevereiro de 2026 |
| Python Mínimo | 3.8 |
| Documentação | 100% atualizada |
| Interface Gráfica | ttk.Notebook (abas) |
| Base de Dados | MySQL/MariaDB |

---

## 🔗 Referências Externas

- [Documentação Python](https://docs.python.org/3/)
- [Tkinter Oficialmente](https://docs.python.org/3/library/tkinter.html)
- [MySQL/MariaDB](https://mariadb.com/kb)
- [bcrypt](https://github.com/pyca/bcrypt)

---

## 📝 Convenções de Documentação

Todos os documentos usam:
- ✅ Markdown (.md) ou Texto (.txt)
- ✅ Unicode ícones para navegação visual
- ✅ Código em blocos formatados
- ✅ Índices e tabelas de conteúdo
- ✅ Links internos entre documentos
- ✅ Português e/ou Inglês

---

**Última Atualização:** 27 de fevereiro de 2026  
**Versão Documentação:** 2.0
