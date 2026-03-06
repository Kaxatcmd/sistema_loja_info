# ⚡ QUICK START - Computer Store System V2.0

Get started with the system in **less than 5 minutes**.

---

## 🚀 3 Steps to Start

### 1️⃣ Install Dependencies

```bash
cd /home/elgz/Documentos/Form_Prog_Python/Eng_Soft
source venv/bin/activate
pip install -r requirements.txt
```

### 2️⃣ Configure Database

```bash
python3 setup_database_v2.py
```

This creates the database with:
- ✅ Tables (clients, products, sales, cart)
- ✅ Indexes for performance
- ✅ 15 computer science products
- ✅ 4 test clients

### 3️⃣ Run Application

```bash
python3 sistema_loja_tkinter.py
```

Window opens → **System ready!**

---

## 👤 Test Users

### Clients (👤)

All with password: `user123`

```
maria@example.com      → Maria Silva
pedro@example.com      → Pedro Santos
ana@example.com        → Ana Costa
carlos@example.com     → Carlos Oliveira
```

### Administrator (▲)

```
Email:    admin@loja.com
Password: admin123
```

---

## 🎯 What to Do

### If You're a Client (👤)

1. **Login** with `maria@example.com` / `user123`
2. **Tab ▸ Explore** → View products
3. **Click "Add to Cart"** for desired computer
4. **Tab ▪ Cart** → View shopping cart
5. **"Checkout" Button** to purchase

### If You're an Admin (▲)

1. **Login** with `admin@loja.com` / `admin123`
2. **Tab ▬ Products** → Manage product inventory
3. **Tab ◩ Clients** → Manage clients
4. **Tab ▣ Sales** → View transaction history

---

## 🎨 Interface

```
┌─────────────────────────────────────┐
│   ⌂ COMPUTER STORE                  │
├─────────────────────────────────────┤
│  ▸ Explore  │  ▪ Cart               │
├──┬──────────────────────────────────┤
│ID│Product    │Price   │Stock │Action│
├──┼──────────────────────────────────┤
│1 │PC 1       │999.99€ │5     │ ⊕   │
│2 │Monitor 4K │299.99€ │12    │ ⊕   │
│3 │Keyboard   │79.99€  │20    │ ⊕   │
└──┴──────────────────────────────────┘
```

---

## ⚠️ Common Issues

### "ModuleNotFoundError: No module named 'mysql'"
```bash
pip install mysql-connector-python
```

### "ModuleNotFoundError: No module named 'bcrypt'"
```bash
pip install bcrypt
```

### "Connection refused" (Database not running)
```bash
sudo service mysql start
```

### Tkinter not working (Linux)
```bash
sudo apt-get install python3-tk
```

---

## 📚 Next Steps

- 📖 See [README_LOJA.md](README_LOJA.md) for full documentation
- 🏗️ See [ARQUITETURA.md](ARQUITETURA.md) to understand the code
- ⚙️ See [CONFIGURACAO.md](CONFIGURACAO.md) for customization

---

**Version:** 2.0  
**Last Updated:** February 27, 2026
