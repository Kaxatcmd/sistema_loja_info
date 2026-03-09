# 🔧 GUIA DE EXTENSÃO - Como Adicionar Novas Features

Instruções para estender o sistema com novas funcionalidades.

---

## 1️⃣ Adicionar Novo Modelo (ex: Avaliação)

### Passo 1: Criar classe em `src/models/avaliacao.py`

```python
"""Modelo de Avaliação"""

class Avaliacao:
    def __init__(self, id_avaliacao=None, id_produto=None, 
                 id_cliente=None, nota=None, comentario=None):
        self.id_avaliacao = id_avaliacao
        self.id_produto = id_produto
        self.id_cliente = id_cliente
        self.nota = nota
        self.comentario = comentario
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id_avaliacao=data.get('id_avaliacao'),
            # ... mais campos
        )
```

### Passo 2: Criar tabela na BD

Editar `setup/database.py` e adicionar:

```python
cursor.execute("""
    CREATE TABLE IF NOT EXISTS avaliacoes (
        id_avaliacao INT PRIMARY KEY AUTO_INCREMENT,
        id_produto INT NOT NULL,
        id_cliente INT NOT NULL,
        nota INT NOT NULL,
        comentario TEXT,
        data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_produto) REFERENCES produtos(id_produto),
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
    )
""")
```

---

## 2️⃣ Adicionar Novo Validador

### Em `src/utils/validators.py`

```python
def validar_nota(nota_str):
    """Valida nota de 1 a 5"""
    if not nota_str:
        return False, None, "Nota é obrigatória"
    
    try:
        nota = int(nota_str)
        if nota < 1 or nota > 5:
            return False, None, "Nota deve estar entre 1 e 5"
        return True, nota, "OK"
    except ValueError:
        return False, None, "Nota deve ser um número inteiro"
```

---

## 3️⃣ Adicionar Nova Tela

### Criar `src/ui/screens/avaliacoes.py`

```python
"""Tela de Avaliações"""

class AvaliacoesScreen:
    def __init__(self, master, db, usuario):
        self.master = master
        self.db = db
        self.usuario = usuario
    
    def show(self):
        """Exibe tela de avaliações"""
        # ... implementar interface
        pass
```

### Adicionar aba em `src/ui/app.py`

```python
# Na interface cliente, adicionar:
frame_avaliacoes = ttk.Frame(self.notebook)
self.notebook.add(frame_avaliacoes, text="★ Avaliações")
self._criar_aba_avaliacoes(frame_avaliacoes)
```

---

## 4️⃣ Adicionar Novo Componente UI

### Em `src/ui/components/widgets.py`

```python
def criar_estrelas(parent, nota, tamanho=20):
    """Cria componente de estrelas para avaliar"""
    canvas = tk.Canvas(parent, height=tamanho, width=tamanho*5, 
                      bg='white', highlightthickness=0)
    canvas.pack()
    
    for i in range(5):
        if i < nota:
            canvas.create_polygon(...)  # Estrela preenchida
        else:
            canvas.create_polygon(...)  # Estrela vazia
    
    return canvas
```

---

## 5️⃣ Adicionar Nova Query à BD

### Em suas operações, use:

```python
# SELECT (query)
avaliacoes = self.db.executar_query(
    "SELECT * FROM avaliacoes WHERE id_produto = %s",
    (id_produto,)
)

# INSERT/UPDATE (update)
resultado = self.db.executar_update(
    "INSERT INTO avaliacoes (...) VALUES (...)",
    (valores,)
)
```

---

## 📋 Checklist para Adicionar Feature

- [ ] Criar modelo em `src/models/`
- [ ] Adicionar validador em `src/utils/validators.py`
- [ ] Criar tabela na BD (setup/database.py)
- [ ] Criar tela em `src/ui/screens/` (se necessário)
- [ ] Implementar componentes em `src/ui/components/` (se necessário)
- [ ] Adicionar aba em `src/ui/app.py` (se necessário)
- [ ] Atualizar CONFIGURACAO.md
- [ ] Testar funcionalidade

---

## 🧪 Testando Localmente

```bash
# Reconfigurar BD com novas tabelas
python setup_db.py

# Executar aplicação
python main.py

# Testar com credenciais de teste
```

---

## 💡 Boas Práticas

✅ **Separar por camadas** - Models, Utils, UI, DB  
✅ **Reutilizar código** - Evitar duplicação  
✅ **Validar sempre** - Dados do utilizador e BD  
✅ **Comentar código** - Especialmente lógica complexa  
✅ **Manter config.py atualizado** - Constantes centralizadas  
✅ **Testar mudanças** - Antes de commit  

---

## ⚠️ Evitar

❌ Lógica de BD em ficheiros UI  
❌ Queries inline (sem prepared statements)  
❌ Passwords em texto plano  
❌ Importações circulares  
❌ Variáveis globais (usar self.)  

---

**Desenvolvendo com estilo! 🎨**
