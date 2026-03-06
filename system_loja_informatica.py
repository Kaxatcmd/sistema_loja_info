"""
Sistema de Loja de Informática
Aplicação com PySimpleGUI e MariaDB
Versão Melhorada com Segurança, Filtros e Exploração Avançada
"""

import PySimpleGUI as sg
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import re
import bcrypt


# ============================================================================
# CONFIGURAÇÃO DE ESTILO
# ============================================================================
sg.theme('DarkBlue3')

FONT_SMALL = ('Helvetica', 10)
FONT_NORMAL = ('Helvetica', 11)
FONT_LARGE = ('Helvetica', 12, 'bold')
FONT_TITLE = ('Helvetica', 14, 'bold')

COLOR_SUCCESS = '#90EE90'
COLOR_ERROR = '#FFB6C6'
COLOR_WARNING = '#FFD700'


# ============================================================================
# FUNÇÕES DE CRIPTOGRAFIA E SEGURANÇA
# ============================================================================
def hash_password(password):
    """Cria um hash seguro da password"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password, password_hash):
    """Verifica se a password corresponde ao hash"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except:
        return False


# ============================================================================
# GESTÃO DE BASE DE DADOS
# ============================================================================
class DatabaseManager:
    """Gerencia conexão e operações com MariaDB"""
    
    def __init__(self, host='localhost', user='root', password='', 
                 database='loja_informatica', unix_socket='/opt/lampp/tmp/mysql.sock'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.unix_socket = unix_socket
        self.connection = None
        
    def conectar(self):
        """Estabelece conexão com a BD"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                use_pure=True
            )
            if self.connection.is_connected():
                print("✔ Conexão estabelecida com sucesso!")
                return True
        except Error as e:
            print(f"✘ Erro ao conectar: {e}")
            return False
    
    def desconectar(self):
        """Fecha conexão com a BD"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✔ Conexão fechada")
    
    def executar_query(self, query, params=None):
        """Executa uma query SELECT"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            resultado = cursor.fetchall()
            cursor.close()
            return resultado
        except Error as e:
            print(f"✘ Erro ao executar query: {e}")
            return None
    
    def executar_update(self, query, params=None):
        """Executa INSERT, UPDATE ou DELETE"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            resultado = cursor.lastrowid
            cursor.close()
            return resultado
        except Error as e:
            self.connection.rollback()
            print(f"✘ Erro ao executar update: {e}")
            return None


# ============================================================================
# FUNÇÕES DE AUTENTICAÇÃO
# ============================================================================
def criar_janela_login():
    """Cria a janela de login"""
    
    layout = [
        [sg.Text('⌂ LOJA DE INFORMÁTICA', font=FONT_TITLE, justification='center')],
        [sg.Text('')],
        [sg.Text('Email:', font=FONT_NORMAL), 
         sg.InputText(key='-EMAIL-', size=(25, 1), font=FONT_NORMAL)],
        [sg.Text('Password:', font=FONT_NORMAL), 
         sg.InputText(key='-PASS-', size=(25, 1), font=FONT_NORMAL, password_char='*')],
        [sg.Text('')],
        [sg.Button('Login', font=FONT_NORMAL, size=(10, 1)),
         sg.Button('Criar Conta', font=FONT_NORMAL, size=(10, 1)),
         sg.Button('Sair', font=FONT_NORMAL, size=(10, 1))],
        [sg.Text('', key='-MSG-', text_color=COLOR_ERROR, font=FONT_SMALL)]
    ]
    
    return sg.Window('Loja de Informática - Login', layout, finalize=True)


def criar_janela_criar_conta():
    """Cria a janela de criação de conta"""
    
    layout = [
        [sg.Text('▥ CRIAR NOVA CONTA', font=FONT_TITLE, justification='center')],
        [sg.Text('')],
        [sg.Text('Nome:', font=FONT_NORMAL), 
         sg.InputText(key='-NOME-', size=(25, 1), font=FONT_NORMAL)],
        [sg.Text('Email:', font=FONT_NORMAL), 
         sg.InputText(key='-EMAIL-', size=(25, 1), font=FONT_NORMAL)],
        [sg.Text('Telefone:', font=FONT_NORMAL), 
         sg.InputText(key='-TELEFONE-', size=(25, 1), font=FONT_NORMAL)],
        [sg.Text('Password:', font=FONT_NORMAL), 
         sg.InputText(key='-PASS-', size=(25, 1), font=FONT_NORMAL, password_char='*')],
        [sg.Text('Confirmar Password:', font=FONT_NORMAL), 
         sg.InputText(key='-PASS2-', size=(25, 1), font=FONT_NORMAL, password_char='*')],
        [sg.Text('')],
        [sg.Button('Registar', font=FONT_NORMAL, size=(10, 1)),
         sg.Button('Cancelar', font=FONT_NORMAL, size=(10, 1))],
        [sg.Text('', key='-MSG-', text_color=COLOR_ERROR, font=FONT_SMALL)]
    ]
    
    return sg.Window('Criar Conta', layout, finalize=True)


def criar_janela_produtos(db, cliente_id):
    """Cria a janela de exploração de produtos com filtros e busca"""
    
    # Buscar produtos
    produtos = db.executar_query("SELECT * FROM produtos WHERE stock > 0 ORDER BY nome")
    if not produtos:
        produtos = []
    
    # Preparar dados para a tabela
    headers = ['Código', 'Nome', 'Preço', 'Stock']
    dados = []
    
    for p in produtos:
        dados.append([
            p['id_produto'], 
            p['nome'][:30], 
            f"{p['preco']:.2f}€", 
            p['stock']
        ])
    
    layout = [
        [sg.Text('▸ EXPLORAR PRODUTOS DA LOJA', font=FONT_TITLE, justification='center')],
        [sg.Text('')],
        
        # Barra de busca e filtros
        [sg.Text('🔍 Buscar:', font=FONT_NORMAL), 
         sg.InputText(key='-BUSCA-', size=(30, 1), font=FONT_NORMAL, enable_events=True),
         sg.Button('🔍 Limpar', font=FONT_NORMAL, size=(8, 1))],
        
        [sg.Text('Preço Máximo (€):', font=FONT_NORMAL), 
         sg.Spin(values=list(range(0, 5000, 100)), initial_value=5000, key='-PRECO_MAX-', 
                size=(10, 1), enable_events=True),
         sg.Text('  |  Ordenar:', font=FONT_NORMAL),
         sg.Combo(['Por Nome ↑', 'Por Nome ↓', 'Por Preço ↑', 'Por Preço ↓'], 
                 default_value='Por Nome ↑', key='-ORDENAR-', size=(15, 1), enable_events=True)],
        
        [sg.Text('')],
        
        # Tabela de produtos
        [sg.Table(values=dados, headings=headers, max_col_widths=[8, 25, 10, 8],
                  key='-TABELA-', font=FONT_NORMAL, size=(50, 12),
                  enable_events=True, right_click_menu=['&Right', ['Ver Detalhes', 'Adicionar ao Carrinho']])],
        
        [sg.Text('Quantidade:', font=FONT_NORMAL), 
         sg.Spin(values=list(range(1, 100)), initial_value=1, key='-QTD-', size=(5, 1))],
        
        [sg.Button('👁️ Ver Detalhes', font=FONT_NORMAL, size=(15, 1)),
         sg.Button('▪ Adicionar ao Carrinho', font=FONT_NORMAL, size=(15, 1)),
         sg.Button('▸ Ver Carrinho', font=FONT_NORMAL, size=(15, 1))],
        
        [sg.Button('◆ Logout', font=FONT_NORMAL, size=(15, 1))],
        
        [sg.Text('', key='-MSG-', text_color=COLOR_SUCCESS, font=FONT_SMALL)]
    ]
    
    return sg.Window('Produtos', layout, finalize=True), produtos


def criar_janela_detalhes_produto(produto):
    """Cria uma janela com detalhes do produto"""
    
    layout = [
        [sg.Text('▬ DETALHES DO PRODUTO', font=FONT_TITLE, justification='center')],
        [sg.Text('')],
        
        [sg.Text('Nome:', font=('Helvetica', 11, 'bold')), 
         sg.Text(produto['nome'], font=FONT_NORMAL, size=(40, 1))],
        
        [sg.Text('Descrição:', font=('Helvetica', 11, 'bold'))],
        [sg.Multiline(produto['descricao'], size=(50, 6), disabled=True, 
                     font=FONT_NORMAL, border_width=1)],
        
        [sg.Text('')],
        
        [sg.Text('Preço:', font=('Helvetica', 11, 'bold')), 
         sg.Text(f"{produto['preco']:.2f}€", font=('Helvetica', 12, 'bold'), 
                text_color='#00AA00')],
        
        [sg.Text('Stock Disponível:', font=('Helvetica', 11, 'bold')), 
         sg.Text(f"{produto['stock']} und.", font=FONT_NORMAL)],
        
        [sg.Text('')],
        
        [sg.Button('Fechar', font=FONT_NORMAL, size=(15, 1))]
    ]
    
    return sg.Window('Detalhes do Produto', layout, finalize=True)


def criar_janela_carrinho(carrinho, db):
    """Cria a janela do carrinho de compras"""
    
    # Preparar dados
    headers = ['Produto', 'Preço Unit.', 'Quantidade', 'Subtotal']
    dados = []
    total = 0
    
    for item in carrinho:
        subtotal = item['preco'] * item['quantidade']
        total += subtotal
        dados.append([item['nome'], f"{item['preco']:.2f}€", 
                     item['quantidade'], f"{subtotal:.2f}€"])
    
    layout = [
        [sg.Text('▪ CARRINHO DE COMPRAS', font=FONT_TITLE, justification='center')],
        [sg.Text('')],
        [sg.Table(values=dados, headings=headers, max_col_widths=[25, 12, 12, 12],
                  key='-CARRINHO-', font=FONT_NORMAL, size=(50, 10))],
        [sg.Text('')],
        [sg.Text(f'TOTAL: {total:.2f}€', font=('Helvetica', 12, 'bold'), 
                text_color='#00FF00')],
        [sg.Text('')],
        [sg.Button('Remover Selecionado', font=FONT_NORMAL, size=(15, 1)),
         sg.Button('Limpar Carrinho', font=FONT_NORMAL, size=(15, 1))],
        [sg.Button('Continuar Compras', font=FONT_NORMAL, size=(15, 1)),
         sg.Button('Finalizar Compra', font=FONT_NORMAL, size=(15, 1))],
        [sg.Text('', key='-MSG-', text_color=COLOR_ERROR, font=FONT_SMALL)]
    ]
    
    return sg.Window('Carrinho', layout, finalize=True), total


# ============================================================================
# VALIDAÇÃO
# ============================================================================
def validar_email(email):
    """Valida formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validar_telefone(telefone):
    """Valida formato de telefone"""
    return len(telefone) >= 9 and telefone.isdigit()


# ============================================================================
# APLICAÇÃO PRINCIPAL
# ============================================================================
class LojaApp:
    """Classe principal da aplicação"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.cliente_atual = None
        self.carrinho = []
        
    def conectar_bd(self):
        """Conecta à base de dados"""
        if not self.db.conectar():
            sg.popup_error('Erro', 'Não foi possível conectar à base de dados!\n\n' +
                          'Certifique-se que:\n' +
                          '1. MariaDB está em execução\n' +
                          '2. Base de dados "loja_informatica" existe\n' +
                          '3. Credenciais estão corretas')
            return False
        return True
    
    def login(self, email, password):
        """Faz login do cliente com validação segura de password"""
        if not email or not password:
            return False, "Email e password são obrigatórios!"
        
        cliente = self.db.executar_query(
            "SELECT * FROM clientes WHERE email = %s",
            (email,)
        )
        
        if not cliente:
            return False, "Email não encontrado! Crie uma conta."
        
        # Validar password com hash
        cliente_data = cliente[0]
        if 'password' not in cliente_data or not cliente_data['password']:
            # Se não tiver password na base (dados antigos), aceita qualquer entrada
            # Isto é apenas para compatibilidade com dados existentes
            return False, "Credenciais inválidas!"
        
        if verify_password(password, cliente_data['password']):
            self.cliente_atual = cliente_data
            return True, f"Bem-vindo, {cliente_data['nome']}!"
        
        return False, "Password incorreta!"
    
    def criar_conta(self, nome, email, telefone, password, password2):
        """Cria nova conta de cliente com password hasheada"""
        
        # Validações
        if not all([nome, email, telefone, password, password2]):
            return False, "Todos os campos são obrigatórios!"
        
        if not validar_email(email):
            return False, "Email inválido!"
        
        if not validar_telefone(telefone):
            return False, "Telefone inválido (min 9 dígitos)!"
        
        if len(password) < 6:
            return False, "Password deve ter pelo menos 6 caracteres!"
        
        if password != password2:
            return False, "Passwords não correspondem!"
        
        # Verificar se email já existe
        existente = self.db.executar_query(
            "SELECT * FROM clientes WHERE email = %s",
            (email,)
        )
        
        if existente:
            return False, "Email já registado!"
        
        # Hash da password
        password_hash = hash_password(password)
        
        # Criar cliente com password hasheada
        id_novo = self.db.executar_update(
            "INSERT INTO clientes (nome, email, telefone, password) VALUES (%s, %s, %s, %s)",
            (nome, email, telefone, password_hash)
        )
        
        if id_novo:
            self.cliente_atual = {
                'id_cliente': id_novo,
                'nome': nome,
                'email': email,
                'telefone': telefone
            }
            return True, f"Conta criada com sucesso! Bem-vindo, {nome}!"
        
        return False, "Erro ao criar conta!"
    
    def adicionar_ao_carrinho(self, produto_id, quantidade, preco, nome):
        """Adiciona produto ao carrinho"""
        item_existente = next((item for item in self.carrinho 
                              if item['id_produto'] == produto_id), None)
        
        if item_existente:
            item_existente['quantidade'] += quantidade
        else:
            self.carrinho.append({
                'id_produto': produto_id,
                'nome': nome,
                'preco': preco,
                'quantidade': quantidade
            })
        
        return True, f"{quantidade}x {nome} adicionado(s) ao carrinho!"
    
    def remover_do_carrinho(self, index):
        """Remove produto do carrinho"""
        if 0 <= index < len(self.carrinho):
            removido = self.carrinho.pop(index)
            return True, f"{removido['nome']} removido do carrinho!"
        return False, "Produto não encontrado!"
    
    def finalizar_compra(self):
        """Finaliza a compra"""
        if not self.carrinho:
            return False, "Carrinho vazio!"
        
        # Calcular total
        total = sum(item['preco'] * item['quantidade'] for item in self.carrinho)
        
        # Criar venda
        id_venda = self.db.executar_update(
            "INSERT INTO vendas (id_cliente, data, total) VALUES (%s, %s, %s)",
            (self.cliente_atual['id_cliente'], datetime.now().date(), total)
        )
        
        if not id_venda:
            return False, "Erro ao criar venda!"
        
        # Adicionar itens da venda
        for item in self.carrinho:
            self.db.executar_update(
                "INSERT INTO venda_produto (id_venda, id_produto, preco) VALUES (%s, %s, %s)",
                (id_venda, item['id_produto'], item['preco'])
            )
            
            # Atualizar stock
            self.db.executar_update(
                "UPDATE produtos SET stock = stock - %s WHERE id_produto = %s",
                (item['quantidade'], item['id_produto'])
            )
        
        self.carrinho = []
        return True, f"Compra finalizada com sucesso! ID: {id_venda}\nTotal: {total:.2f}€"
    
    def cancelar_compra(self):
        """Cancela a compra atual"""
        self.carrinho = []
        return True, "Compra cancelada! Voltemos a explorar..."
    
    def filtrar_produtos(self, produtos, busca="", preco_max=5000, ordem="nome_asc"):
        """Filtra e ordena produtos de acordo com critérios"""
        
        # Aplicar filtro de busca
        if busca:
            produtos_filtrados = [p for p in produtos 
                                 if busca.lower() in p['nome'].lower() or 
                                    busca.lower() in p['descricao'].lower()]
        else:
            produtos_filtrados = produtos.copy()
        
        # Aplicar filtro de preço
        produtos_filtrados = [p for p in produtos_filtrados if p['preco'] <= preco_max]
        
        # Aplicar ordenação
        if ordem == "nome_desc":
            produtos_filtrados.sort(key=lambda x: x['nome'], reverse=True)
        elif ordem == "preco_asc":
            produtos_filtrados.sort(key=lambda x: x['preco'])
        elif ordem == "preco_desc":
            produtos_filtrados.sort(key=lambda x: x['preco'], reverse=True)
        else:  # nome_asc (padrão)
            produtos_filtrados.sort(key=lambda x: x['nome'])
        
        return produtos_filtrados
    
    def get_produtos_tabela(self, produtos):
        """Converte lista de produtos para formato de tabela"""
        headers = ['Código', 'Nome', 'Preço', 'Stock']
        dados = []
        
        for p in produtos:
            dados.append([
                p['id_produto'], 
                p['nome'][:30], 
                f"{p['preco']:.2f}€", 
                p['stock']
            ])
        
        return headers, dados
    
    def run(self):
        """Executa a aplicação"""
        
        if not self.conectar_bd():
            return
        
        # Janela de login
        janela_login = criar_janela_login()
        
        while True:
            event, values = janela_login.read()
            
            if event == sg.WINDOW_CLOSED or event == 'Sair':
                break
            
            elif event == 'Login':
                email = values['-EMAIL-'].strip()
                password = values['-PASS-'].strip()
                
                sucesso, msg = self.login(email, password)
                
                if sucesso:
                    janela_login['-MSG-'].update(msg, text_color=COLOR_SUCCESS)
                    janela_login.hide()
                    self.loop_cliente()
                    janela_login.un_hide()
                    janela_login['-EMAIL-'].update('')
                    janela_login['-PASS-'].update('')
                else:
                    janela_login['-MSG-'].update(msg, text_color=COLOR_ERROR)
            
            elif event == 'Criar Conta':
                janela_login.hide()
                if self.loop_criar_conta():
                    janela_login.un_hide()
                    self.loop_cliente()
                janela_login.un_hide()
        
        janela_login.close()
        self.db.desconectar()
    
    def loop_criar_conta(self):
        """Loop para criar conta"""
        janela = criar_janela_criar_conta()
        
        while True:
            event, values = janela.read()
            
            if event == sg.WINDOW_CLOSED or event == 'Cancelar':
                break
            
            elif event == 'Registar':
                nome = values['-NOME-'].strip()
                email = values['-EMAIL-'].strip()
                telefone = values['-TELEFONE-'].strip()
                password = values['-PASS-'].strip()
                password2 = values['-PASS2-'].strip()
                
                sucesso, msg = self.criar_conta(nome, email, telefone, password, password2)
                
                if sucesso:
                    janela['-MSG-'].update(msg, text_color=COLOR_SUCCESS)
                    janela.read(timeout=2000)
                    break
                else:
                    janela['-MSG-'].update(msg, text_color=COLOR_ERROR)
        
        janela.close()
        return self.cliente_atual is not None
    
    def loop_cliente(self):
        """Loop principal do cliente com exploração avançada de produtos"""
        janela_produtos, todos_produtos = criar_janela_produtos(self.db, self.cliente_atual['id_cliente'])
        produtos_atuais = todos_produtos.copy()
        
        while True:
            event, values = janela_produtos.read()
            
            if event == sg.WINDOW_CLOSED or event == '◆ Logout':
                break
            
            # Eventos de filtro e busca
            elif event == '-BUSCA-' or event == '-PRECO_MAX-' or event == '-ORDENAR-':
                busca = values['-BUSCA-'].strip()
                preco_max = int(values['-PRECO_MAX-'])
                ordem_map = {
                    'Por Nome ↑': 'nome_asc',
                    'Por Nome ↓': 'nome_desc',
                    'Por Preço ↑': 'preco_asc',
                    'Por Preço ↓': 'preco_desc'
                }
                ordem = ordem_map.get(values['-ORDENAR-'], 'nome_asc')
                
                # Filtrar produtos
                produtos_atuais = self.filtrar_produtos(todos_produtos, busca, preco_max, ordem)
                
                # Atualizar tabela
                headers, dados = self.get_produtos_tabela(produtos_atuais)
                janela_produtos['-TABELA-'].update(values=dados)
                
                quantidade = len(produtos_atuais)
                janela_produtos['-MSG-'].update(
                    f"✔ {quantidade} produto(s) encontrado(s)",
                    text_color=COLOR_SUCCESS
                )
            
            elif event == 'Limpar':
                janela_produtos['-BUSCA-'].update('')
                janela_produtos['-PRECO_MAX-'].update(5000)
                janela_produtos['-ORDENAR-'].update('Por Nome ↑')
                produtos_atuais = todos_produtos.copy()
                headers, dados = self.get_produtos_tabela(produtos_atuais)
                janela_produtos['-TABELA-'].update(values=dados)
                janela_produtos['-MSG-'].update(f"✔ Filtros limpos ({len(produtos_atuais)} produtos)", 
                                               text_color=COLOR_SUCCESS)
            
            # Ver detalhes do produto
            elif event == '👁️ Ver Detalhes':
                if values['-TABELA-']:
                    try:
                        row = values['-TABELA-'][0]
                        produto = produtos_atuais[row]
                        
                        janela_detalhes = criar_janela_detalhes_produto(produto)
                        janela_detalhes.read()
                        janela_detalhes.close()
                    except IndexError:
                        janela_produtos['-MSG-'].update("Selecione um produto!", 
                                                       text_color=COLOR_ERROR)
                else:
                    janela_produtos['-MSG-'].update("Selecione um produto!", 
                                                   text_color=COLOR_ERROR)
            
            # Adicionar ao carrinho
            elif event == '▪ Adicionar ao Carrinho':
                if values['-TABELA-']:
                    try:
                        row = values['-TABELA-'][0]
                        produto = produtos_atuais[row]
                        qtd = int(values['-QTD-'])
                        
                        if qtd > produto['stock']:
                            janela_produtos['-MSG-'].update(
                                f"Stock insuficiente! Disponível: {produto['stock']}",
                                text_color=COLOR_ERROR
                            )
                        elif qtd <= 0:
                            janela_produtos['-MSG-'].update(
                                "Quantidade deve ser maior que 0!",
                                text_color=COLOR_ERROR
                            )
                        else:
                            sucesso, msg = self.adicionar_ao_carrinho(
                                produto['id_produto'],
                                qtd,
                                produto['preco'],
                                produto['nome']
                            )
                            
                            janela_produtos['-MSG-'].update(msg, 
                                text_color=COLOR_SUCCESS if sucesso else COLOR_ERROR)
                    except (IndexError, ValueError):
                        janela_produtos['-MSG-'].update("Erro ao adicionar! Verifique a quantidade.", 
                                                       text_color=COLOR_ERROR)
                else:
                    janela_produtos['-MSG-'].update("Selecione um produto!", 
                                                   text_color=COLOR_ERROR)
            
            # Ver carrinho
            elif event == '▸ Ver Carrinho':
                janela_produtos.hide()
                self.loop_carrinho()
                janela_produtos.un_hide()
        
        janela_produtos.close()
    
    def loop_carrinho(self):
        """Loop do carrinho de compras"""
        while True:
            janela_carrinho, total = criar_janela_carrinho(self.carrinho, self.db)
            
            event, values = janela_carrinho.read()
            
            if event == sg.WINDOW_CLOSED or event == 'Continuar Compras':
                break
            
            elif event == 'Remover Selecionado':
                if values['-CARRINHO-']:
                    row = values['-CARRINHO-'][0]
                    sucesso, msg = self.remover_do_carrinho(row)
                    janela_carrinho['-MSG-'].update(msg,
                        text_color=COLOR_SUCCESS if sucesso else COLOR_ERROR)
                else:
                    janela_carrinho['-MSG-'].update("Selecione um produto!",
                        text_color=COLOR_ERROR)
            
            elif event == 'Limpar Carrinho':
                if sg.popup_yes_no('Confirmar', 'Tem certeza que deseja limpar o carrinho?') == 'Yes':
                    self.carrinho = []
                    janela_carrinho['-MSG-'].update("Carrinho limpo!",
                        text_color=COLOR_SUCCESS)
            
            elif event == 'Finalizar Compra':
                sucesso, msg = self.finalizar_compra()
                
                if sucesso:
                    sg.popup_ok('Sucesso', msg, title='Compra Finalizada')
                    break
                else:
                    janela_carrinho['-MSG-'].update(msg, text_color=COLOR_ERROR)
            
            janela_carrinho.close()


# ============================================================================
# MAIN
# ============================================================================
if __name__ == '__main__':
    app = LojaApp()
    app.run()
