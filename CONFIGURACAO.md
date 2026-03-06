# ⚙️ GUIA DE CONFIGURAÇÃO - V2.0

## 📋 Checklist de Instalação

- [ ] Python 3.8+ instalado
- [ ] Repositório clonado/descompactado
- [ ] Ambiente virtual criado
- [ ] Dependências instaladas
- [ ] MariaDB/MySQL instalado
- [ ] Base de dados configurada
- [ ] Aplicação testada

---

## 🔧 Instalação Passo-a-Passo

### 1. Verificar Python
```bash
python3 --version
# Deve ser >= 3.8
```

### 2. Criar Ambiente Virtual
```bash
cd /path/to/Eng_Soft
python3 -m venv venv
```

### 3. Ativar Ambiente Virtual
```bash
# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 4. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 5. Instalar MariaDB (se necessário)
```bash
# Ubuntu/Debian
sudo apt-get install mariadb-server

# Mac (com Homebrew)
brew install mariadb

# Windows
# Descarregar de: https://mariadb.org/download/
```

### 6. Iniciar MariaDB
```bash
# Linux
sudo service mysql start

# Mac
brew services start mariadb

# Windows
# Usar Services ou MariaDB Client
```

### 7. Configurar Base de Dados
```bash
python3 setup_database_v2.py
```

Se tudo correr bem:
```
✔ BASE DE DADOS CONFIGURADA COM SUCESSO!
```

### 8. Executar Aplicação
```bash
python3 sistema_loja_tkinter.py
```

---

## 🗄️ Configuração de Base de Dados

### Parâmetros Padrão
```python
# Em DatabaseManager.__init__()
host='localhost'
user='root'
password=''
database='loja_informatica'
```

### Mudar Configurações

Se o seu MariaDB tem senha ou está num servidor remoto, edite `sistema_loja_tkinter.py`:

```python
class DatabaseManager:
    def __init__(self, host='seu_servidor', 
                 user='seu_usuario', 
                 password='sua_senha', 
                 database='loja_informatica'):
        ...
```

---

## 🔐 Configuração de Segurança

### 1. Mudar Password do Root (Recomendado)
```bash
mysqladmin -u root password "nova_senha"
```

### 2. Ajustar Credenciais na Aplicação
```python
self.db = DatabaseManager(
    host='localhost',
    user='root',
    password='nova_senha',  # ← Alterar aqui
    database='loja_informatica'
)
```

### 3. Criar Utilizador Específico (Melhor Prática)
```sql
CREATE USER 'loja_user'@'localhost' IDENTIFIED BY 'loja_password';
GRANT ALL PRIVILEGES ON loja_informatica.* TO 'loja_user'@'localhost';
FLUSH PRIVILEGES;
```

Depois altere:
```python
self.db = DatabaseManager(
    host='localhost',
    user='loja_user',
    password='loja_password',
    database='loja_informatica'
)
```

---

## 🌐 Servidor Remoto

Para conectar a um servidor MariaDB remoto:

```python
self.db = DatabaseManager(
    host='seu_servidor.com',  # IP ou domínio
    user='seu_usuario',
    password='sua_senha',
    database='loja_informatica',
    port=3306  # Porta padrão
)
```

---

## 📦 Dependências (requirements.txt)

```
mysql-connector-python==8.0.33
bcrypt==4.0.1
```

Para instalar manualmente:
```bash
pip install mysql-connector-python==8.0.33
pip install bcrypt==4.0.1
```

---

## 🧪 Testar Instalação

### 1. Testar Conexão BD
```bash
python3 -c "
import mysql.connector
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    database='loja_informatica'
)
print('✔ Conexão OK')
conn.close()
"
```

### 2. Testar Aplicação (modo teste)
```bash
python3 sistema_loja_tkinter.py
```

Se a janela abrir → Sucesso!

---

## 🐛 Resolução de Problemas

### "ModuleNotFoundError: No module named 'mysql'"

**Solução:**
```bash
pip install mysql-connector-python
```

### "ModuleNotFoundError: No module named 'bcrypt'"

**Solução:**
```bash
pip install bcrypt
```

### "Error connecting to MariaDB"

**Verificar:**
1. MariaDB está em execução?
   ```bash
   sudo service mysql status
   ```

2. Port 3306 está aberta?
   ```bash
   sudo netstat -tuln | grep 3306
   ```

3. Credenciais estão corretas?
   ```bash
   mysql -u root -p
   ```

### "Database 'loja_informatica' não existe"

**Solução:**
```bash
python3 setup_database_v2.py
```

### Tkinter não funciona

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-tk
```

**Mac:**
```bash
brew install python-tk
```

**Windows:**
Reinstale Python e selecione "tcl/tk e IDLE" durante instalação

---

## 📊 Variáveis de Ambiente (Opcional)

Para maior segurança, use variáveis de ambiente:

```bash
# .env file (não fazer commit!)
DB_HOST=localhost
DB_USER=loja_user
DB_PASSWORD=loja_password
DB_NAME=loja_informatica
```

Na aplicação:
```python
import os
from dotenv import load_dotenv

load_dotenv()

self.db = DatabaseManager(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME')
)
```

---

## 🔄 Backup & Restore

### Fazer Backup
```bash
mysqldump -u root loja_informatica > backup.sql
```

### Restaurar Backup
```bash
mysql -u root loja_informatica < backup.sql
```

---

## 📈 Performance

### Índices (já criados automaticamente)
```sql
CREATE INDEX idx_cliente_email ON clientes(email);
CREATE INDEX idx_venda_cliente ON vendas(id_cliente);
CREATE INDEX idx_venda_data ON vendas(data);
```

### Validação de Índices
```sql
SHOW INDEXES FROM clientes;
SHOW INDEXES FROM produtos;
SHOW INDEXES FROM vendas;
```

---

## 🚀 Modo de Produção

### Modificações Recomendadas

1. **Desativar modo de desenvolvimento**
2. **Usar conexão em pool**
3. **Adicionar logging**
4. **Validação rigorosa de entrada**
5. **HTTPS para dados sensíveis** (se web)

---

## 📝 Checklist Final

Antes de ir para produção:

- [ ] Backup da base de dados realizado
- [ ] Credenciais mudadas (não use root)
- [ ] Índices verificados
- [ ] Aplicação testada com dados reais
- [ ] Logs configurados
- [ ] Documentação atualizada

---

## 📞 Suporte

Se tiver dúvidas sobre configuração:

1. Consulte `00_LEIA-ME-PRIMEIRO.txt`
2. Verifique `ARQUITETURA.md`
3. Procure por mensagens de erro na consola
4. Examine logs do MariaDB

---

**Última Atualização:** 27 de fevereiro de 2026  
**Versão:** 2.0
