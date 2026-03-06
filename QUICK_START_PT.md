# ⚡ GUIA RÁPIDO - Sistema de Loja V2.0

Começar a usar o sistema em **menos de 5 minutos**.

---

## 🚀 3 Passos para Começar

### 1️⃣ Instalar Dependências

```bash
cd /home/elgz/Documentos/Form_Prog_Python/Eng_Soft
source venv/bin/activate
pip install -r requirements.txt
```

### 2️⃣ Configurar Base de Dados

```bash
python3 setup_database_v2.py
```

Isto cria a BD com:
- ✅ Tabelas (clientes, produtos, vendas, carrinho)
- ✅ Índices para performance
- ✅ 15 produtos informáticos
- ✅ 4 clientes de teste

### 3️⃣ Executar Aplicação

```bash
python3 sistema_loja_tkinter.py
```

A janela abre → **Sistema pronto!**

---

## 👤 Utilizadores de Teste

### Clientes (👤)

Todos com password: `user123`

```
maria@example.com      → Maria Silva
pedro@example.com      → Pedro Santos
ana@example.com        → Ana Costa
carlos@example.com     → Carlos Oliveira
```

### Administrador (▲)

```
Email:    admin@loja.com
Password: admin123
```

---

## 🎯 O Que Fazer

### Se é Cliente (👤)

1. **Login** com `maria@example.com` / `user123`
2. **Aba ▸ Explorar** → Ver produtos
3. **Clique em "Adicionar ao Carrinho"** para pelo computador desejado
4. **Aba ▪ Carrinho** → Ver carrinho
5. **Botão "Finalizar Compra"** para comprar

### Se é Admin (▲)

1. **Login** com `admin@loja.com` / `admin123`
2. **Aba ▬ Produtos** → Gerir stock de computadores
3. **Aba ◩ Clientes** → Gerir clientes
4. **Aba ▣ Vendas** → Ver histórico de transações

---

## 🎨 Interface

```
┌─────────────────────────────────────┐
│   ⌂ LOJA DE INFORMÁTICA             │
├─────────────────────────────────────┤
│  ▸ Explorar  │  ▪ Carrinho          │
├──┬──────────────────────────────────┤
│ID│Produto    │Preço    │Stock │Ação│
├──┼──────────────────────────────────┤
│1 │PC 1       │999.99€  │5     │ ⊕  │
│2 │Monitor 4K │299.99€  │12    │ ⊕  │
│3 │Teclado    │79.99€   │20    │ ⊕  │
└──┴──────────────────────────────────┘
```

---

## ⚠️ Problemas Comuns

### "ModuleNotFoundError: No module named 'mysql'"
```bash
pip install mysql-connector-python
```

### "ModuleNotFoundError: No module named 'bcrypt'"
```bash
pip install bcrypt
```

### "Connection refused" (BD não está)
```bash
sudo service mysql start
```

### Tkinter não funciona (Linux)
```bash
sudo apt-get install python3-tk
```

---

## 📚 Próximos Passos

- 📖 Ver [00_LEIA-ME-PRIMEIRO.txt](00_LEIA-ME-PRIMEIRO.txt) para mais detalhe
- 🏗️ Ver [ARQUITETURA.md](ARQUITETURA.md) para entender o código
- ⚙️ Ver [CONFIGURACAO.md](CONFIGURACAO.md) para customizar

---

**Versão:** 2.0  
**Última Atualização:** 27 de fevereiro de 2026
