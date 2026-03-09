"""
Utilitários de Segurança
Funções para hash e verificação de passwords
"""

import bcrypt


def hash_password(password):
    """
    Cria hash seguro de password com bcrypt
    
    Args:
        password (str): Password em texto plano
        
    Returns:
        str: Hash da password
    """
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password, password_hash):
    """
    Verifica se password corresponde ao hash
    
    Args:
        password (str): Password em texto plano
        password_hash (str): Hash armazenado
        
    Returns:
        bool: True se password corresponde, False caso contrário
    """
    try:
        if not password_hash:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False
