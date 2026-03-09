"""
Funções de Validação
Validadores para dados da aplicação
"""

import re
from src.config import EMAIL_PATTERN, PASSWORD_MIN_LENGTH


def validar_email(email):
    """
    Valida formato de email
    
    Args:
        email (str): Email a validar
        
    Returns:
        tuple: (bool válido, str mensagem)
    """
    email = email.strip()
    if not email:
        return False, "Email é obrigatório"
    
    if not re.match(EMAIL_PATTERN, email):
        return False, "Formato de email inválido"
    
    return True, "OK"


def validar_password(password):
    """
    Valida password
    
    Args:
        password (str): Password a validar
        
    Returns:
        tuple: (bool válido, str mensagem)
    """
    if not password:
        return False, "Password é obrigatória"
    
    if len(password) < PASSWORD_MIN_LENGTH:
        return False, f"Password deve ter pelo menos {PASSWORD_MIN_LENGTH} caracteres"
    
    return True, "OK"


def validar_preco(preco_str):
    """
    Valida preço
    
    Args:
        preco_str (str): Preço em formato string
        
    Returns:
        tuple: (bool válido, float preço ou None, str mensagem)
    """
    if not preco_str:
        return False, None, "Preço é obrigatório"
    
    try:
        preco = float(preco_str.replace(',', '.'))
        if preco < 0:
            return False, None, "Preço não pode ser negativo"
        return True, preco, "OK"
    except ValueError:
        return False, None, "Preço inválido! Use formato número decimal."


def validar_stock(stock_str):
    """
    Valida stock
    
    Args:
        stock_str (str): Stock em formato string
        
    Returns:
        tuple: (bool válido, int stock ou None, str mensagem)
    """
    if not stock_str:
        return False, None, "Stock é obrigatório"
    
    try:
        stock = int(stock_str)
        if stock < 0:
            return False, None, "Stock não pode ser negativo"
        return True, stock, "OK"
    except ValueError:
        return False, None, "Stock inválido! Use número inteiro."


def validar_nome_produto(nome):
    """
    Valida nome de produto
    
    Args:
        nome (str): Nome a validar
        
    Returns:
        tuple: (bool válido, str mensagem)
    """
    from src.config import PRODUTO_NOME_MAX_LENGTH
    
    if not nome:
        return False, "Nome do produto é obrigatório"
    
    if len(nome) > PRODUTO_NOME_MAX_LENGTH:
        return False, f"Nome muito longo (máx. {PRODUTO_NOME_MAX_LENGTH} caracteres)"
    
    return True, "OK"
