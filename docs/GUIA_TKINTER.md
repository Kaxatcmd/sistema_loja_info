# 🖥️ GUIA TÉCNICO - TKINTER & INTERFACE V2.0

## 📌 O que é Tkinter?

**Tkinter** é a biblioteca gráfica padrão do Python:

- ✅ Nativa do Python 3.x (sem instalação extra)
- ✅ Multiplataforma (Windows, Mac, Linux)
- ✅ Estável e mantida oficialmente
- ✅ Integra-se perfeitamente com código Python puro

---

## 🎨 Widgets Principais Usados

### Layouts
```python
import tkinter as tk
from tkinter import ttk

# Frame - Container genérico
frame = tk.Frame(root, bg='white')
frame.pack(fill=tk.BOTH, expand=True)

# ttk.Frame - Frame moderno
frame = ttk.Frame(root)
frame.pack()
```

### Labels (Texto)
```python
# tk.Label - Básico
label = tk.Label(root, text="Olá", font=("Arial", 12))
label.pack()

# ttk.Label - Moderno
label = ttk.Label(root, text="Olá")
label.pack()
```

### Inputs
```python
# tk.Entry - Campo de texto
entry = tk.Entry(root, width=30)
entry.pack()
valor = entry.get()

# ttk.Entry - Campo moderno
entry = ttk.Entry(root, width=30)
entry.pack()
```

### Buttons
```python
# tk.Button
button = tk.Button(root, text="Clique", command=funcao)
button.pack()

# ttk.Button - Moderno
button = ttk.Button(root, text="Clique", command=funcao)
button.pack()
```

### Listbox
```python
listbox = tk.Listbox(root, height=10)
listbox.insert(tk.END, "Item 1")
listbox.insert(tk.END, "Item 2")
listbox.pack(fill=tk.BOTH, expand=True)

# Obter seleção
selecionado = listbox.curselection()
if selecionado:
    valor = listbox.get(selecionado[0])
```

### Treeview (Tabelas)
```python
tree = ttk.Treeview(root, columns=('Nome', 'Email'), height=10)
tree.heading('#0', text='ID')
tree.heading('Nome', text='Nome Completo')
tree.heading('Email', text='Email')

tree.insert('', tk.END, text='1', values=('João Silva', 'joao@example.com'))
tree.insert('', tk.END, text='2', values=('Maria Santos', 'maria@example.com'))

tree.pack(fill=tk.BOTH, expand=True)
```

### MessageBox (Diálogos)
```python
from tkinter import messagebox

messagebox.showinfo("Título", "Mensagem informativa")
messagebox.showwarning("Aviso", "Mensagem de aviso")
messagebox.showerror("Erro", "Mensagem de erro")

resposta = messagebox.askyesno("Pergunta", "Tem a certeza?")
if resposta:
    print("Utilizador clicou Sim")
```

---

## 📑 ttk.Notebook - Abas

Componente principal da versão 2.0:

```python
from tkinter import ttk

# Criar notebook (abas)
notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True)

# Criar aba 1
aba1 = ttk.Frame(notebook)
notebook.add(aba1, text="▸ Explorar")

# Adicionar widgets à aba 1
label = ttk.Label(aba1, text="Conteúdo da aba 1")
label.pack()

# Criar aba 2
aba2 = ttk.Frame(notebook)
notebook.add(aba2, text="▪ Carrinho")

# Adicionar widgets à aba 2
label = ttk.Label(aba2, text="Conteúdo da aba 2")
label.pack()
```

### Obtendo Aba Selecionada

```python
def aba_mudou(event):
    aba_atual = notebook.index("current")
    print(f"Aba {aba_atual} selecionada")

notebook.bind("<<NotebookTabChanged>>", aba_mudou)
```

### Atualizar Conteúdo de Aba

```python
def atualizar_aba_carrinho():
    """Limpa e redesenha a aba do carrinho"""
    
    # Limpar widgets antigos
    for widget in aba_carrinho.winfo_children():
        widget.destroy()
    
    # Redesenhar com novos dados
    for item in self.carrinho:
        label = ttk.Label(aba_carrinho, text=f"{item['nome']} - €{item['preco']}")
        label.pack()

# Chamar quando carrinho muda
atualizar_aba_carrinho()
```

---

## 🎯 Gestão de Layout

### Pack Geometry
```python
widget.pack(
    side=tk.LEFT,           # LEFT, RIGHT, TOP, BOTTOM
    fill=tk.BOTH,          # X, Y, BOTH
    expand=True,           # Expandir espaço disponível
    padx=10,               # Espaco horizontal
    pady=10                # Espaco vertical
)
```

### Grid Geometry (Tabelas)
```python
widget.grid(
    row=0,                 # Linha (vertical)
    column=0,              # Coluna (horizontal)
    sticky='ew',           # E (Este), W (Oeste), N, S
    padx=5,
    pady=5
)

# Configurar pesos das linhas/colunas (para responsivo)
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
```

### Place (Absoluto)
```python
widget.place(
    x=100, y=100,          # Posição X, Y
    width=200, height=50   # Tamanho
)
```

---

## 🎨 Temas e Estilos

### Tema ttk

```python
import tkinter as tk
from tkinter import ttk

root = tk.Tk()

# Listar temas disponíveis
print(ttk.Style().theme_names())  # ['default', 'clam', 'alt', 'classic']

# Usar tema específico
style = ttk.Style()
style.theme_use('clam')
```

### Cores Personalizadas

```python
# Cores nomeadas
label = tk.Label(root, text="Texto", bg='white', fg='black')

# Cores em HEX
label = tk.Label(root, text="Texto", bg='#FFFFFF', fg='#000000')

# RGB (menos comum)
label = tk.Label(root, text="Texto", bg='rgb(255, 255, 255)')
```

### Fonts

```python
import tkinter.font as tkFont

# Fonte padrão
default_font = ("Arial", 12)

# Fonte em negrito
bold_font = ("Arial", 12, "bold")

# Fonte em itálico
italic_font = ("Arial", 12, "italic")

# Combinação
special_font = ("Arial", 12, "bold italic")

# Usar
label = tk.Label(root, text="Texto", font=bold_font)
```

---

## 🔄 Variáveis do Tkinter

```python
from tkinter import tk, StringVar, IntVar, BooleanVar

# StringVar - Texto
var_nome = StringVar(value="João")

# Usar em Entry
entry = tk.Entry(root, textvariable=var_nome)

# Obter valor
print(var_nome.get())  # "João"

# Alterar valor
var_nome.set("Maria")

# IntVar - Números
var_idade = IntVar(value=25)

# BooleanVar - Booleano
var_ativo = BooleanVar(value=True)

# Saber quando muda (callback)
def on_change(*args):
    print(f"Novo valor: {var_nome.get()}")

var_nome.trace_add('write', on_change)
```

---

## 🔐 Segurança em Input

```python
def validar_email(email):
    """Valida formato de email"""
    import re
    padrão = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(padrão, email) is not None

def validar_numero(valor):
    """Valida se é número"""
    try:
        float(valor)
        return True
    except ValueError:
        return False

# Usar
if validar_email(entry_email.get()):
    print("Email válido")
else:
    messagebox.showerror("Erro", "Email inválido")
```

---

## 📱 Responsividade

```python
def on_resize(event):
    print(f"Nova janela: {event.width}x{event.height}")

root.bind('<Configure>', on_resize)
```

### Layout Responsivo

```python
# Usar pesos de grid para responsividade
root.grid_rowconfigure(0, weight=1)  # Linha 0 expande
root.grid_columnconfigure(0, weight=1)  # Coluna 0 expande

frame = ttk.Frame(root)
frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

# Widgets dentro são responsivos via pack/grid
```

---

## 🧵 Multithreading (Operações Longas)

```python
import threading
from tkinter import messagebox

def operacao_longa():
    """Executar em thread separada"""
    import time
    time.sleep(5)  # Simular operação longa
    messagebox.showinfo("Pronto", "Operação concluída!")

# NÃO CONGELAR INTERFACE
def iniciar_operacao():
    thread = threading.Thread(target=operacao_longa)
    thread.daemon = True  # Fechar com programa
    thread.start()

button = tk.Button(root, text="Iniciar", command=iniciar_operacao)
button.pack()
```

---

## 🔗 Integração com BD

```python
# Método seguro com prepared statements
def obter_cliente(email):
    try:
        resultado = db.executar_query(
            "SELECT * FROM clientes WHERE email = %s",
            (email,)
        )
        return resultado[0] if resultado else None
    except Exception as e:
        messagebox.showerror("Erro BD", str(e))
        return None

# Usar na interface
def buscar_cliente():
    email = entry_email.get().strip()
    if not email:
        messagebox.showwarning("Aviso", "Insira um email")
        return
    
    cliente = obter_cliente(email)
    if cliente:
        label_resultado.config(text=f"Cliente: {cliente['nome']}")
    else:
        label_resultado.config(text="Cliente não encontrado")
```

---

## 🎟️ Exemplo Completo: Mini-Aplicação

```python
import tkinter as tk
from tkinter import ttk, messagebox

class MiniApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mini Aplicação")
        self.root.geometry("400x300")
        
        # Criar interface
        self.criar_widgets()
    
    def criar_widgets(self):
        # Frame principal
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Label
        ttk.Label(frame, text="Nome:").grid(row=0, column=0, sticky='w')
        self.entry_nome = ttk.Entry(frame, width=30)
        self.entry_nome.grid(row=0, column=1, padx=5)
        
        # Label
        ttk.Label(frame, text="Email:").grid(row=1, column=0, sticky='w', pady=5)
        self.entry_email = ttk.Entry(frame, width=30)
        self.entry_email.grid(row=1, column=1, padx=5)
        
        # Botão
        ttk.Button(frame, text="Guardar", command=self.guardar).grid(row=2, column=1, sticky='e', pady=10)
    
    def guardar(self):
        nome = self.entry_nome.get().strip()
        email = self.entry_email.get().strip()
        
        if not nome or not email:
            messagebox.showwarning("Aviso", "Preencha todos os campos")
            return
        
        messagebox.showinfo("Sucesso", f"✔ Guardado: {nome}")
        self.entry_nome.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = MiniApp(root)
    root.mainloop()
```

---

## 📚 Referência Rápida

| Widget | Uso | Exemplo |
|--------|-----|---------|
| Label | Texto estático | `ttk.Label(text="Olá")` |
| Entry | Campo de texto | `ttk.Entry(width=30)` |
| Button | Botão | `ttk.Button(text="OK", command=func)` |
| Listbox | Lista | `tk.Listbox(height=10)` |
| Treeview | Tabela | `ttk.Treeview(columns=())` |
| Frame | Container | `ttk.Frame()` |
| Notebook | Abas | `ttk.Notebook()` |

---

## 🔗 Recursos Oficiais

- [Tkinter Docs](https://docs.python.org/3/library/tkinter.html)
- [ttk Widget Reference](https://www.tcl.tk/man/tcl8.6/TkCmd/ttk_widgets.htm)
- [Tcl/Tk Documentation](https://www.tcl.tk/man/)

---

**Última Atualização:** 27 de fevereiro de 2026  
**Versão:** 2.0
