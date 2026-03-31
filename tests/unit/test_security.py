"""
Testes Unitários — src/utils/security.py

Cobre:
  - hash_password: produz hash bcrypt válido
  - verify_password: verifica password correcta e incorrecta
  - Casos de fronteira (hash None, string vazia, tipos inesperados)
"""

import pytest
from src.utils.security import hash_password, verify_password


# ======================================================================
# hash_password
# ======================================================================

class TestHashPassword:
    """Testes para a função ``hash_password``."""

    def test_hash_nao_e_texto_claro(self):
        """O hash devolvido não deve ser igual à password original."""
        password = "minha_senha_segura"
        resultado = hash_password(password)
        assert resultado != password

    def test_hash_e_string(self):
        """O hash deve ser uma string."""
        resultado = hash_password("qualquer")
        assert isinstance(resultado, str)

    def test_hash_tem_prefixo_bcrypt(self):
        """O hash bcrypt começa sempre com $2b$ ou $2a$."""
        resultado = hash_password("teste123")
        assert resultado.startswith("$2b$") or resultado.startswith("$2a$")

    def test_hashes_diferentes_para_mesma_password(self):
        """
        Dois hashes da mesma password devem ser diferentes (devido ao salt
        aleatório). Isto confirma que o salt está a ser gerado correctamente.
        """
        hash1 = hash_password("abc123")
        hash2 = hash_password("abc123")
        assert hash1 != hash2

    def test_hash_password_longa(self):
        """Hash de password longa deve funcionar sem erros."""
        password_longa = "P@ssw0rd_" * 10
        resultado = hash_password(password_longa)
        assert resultado.startswith("$2b$") or resultado.startswith("$2a$")


# ======================================================================
# verify_password
# ======================================================================

class TestVerifyPassword:
    """Testes para a função ``verify_password``."""

    def test_password_correta(self):
        """verify_password deve devolver True para a password correcta."""
        password = "senha_correcta_42"
        hash_gerado = hash_password(password)
        assert verify_password(password, hash_gerado) is True

    def test_password_incorreta(self):
        """verify_password deve devolver False para password errada."""
        hash_gerado = hash_password("senha_correcta")
        assert verify_password("senha_errada", hash_gerado) is False

    def test_password_vazia_vs_hash_valido(self):
        """Password vazia não deve corresponder a um hash de password normal."""
        hash_gerado = hash_password("senha123")
        assert verify_password("", hash_gerado) is False

    def test_hash_none_devolve_false(self):
        """Se o hash for None, deve devolver False sem lançar excepção."""
        assert verify_password("qualquer", None) is False

    def test_hash_vazio_devolve_false(self):
        """Se o hash for string vazia, deve devolver False."""
        assert verify_password("qualquer", "") is False

    def test_hash_invalido_devolve_false(self):
        """Hash corrompido/inválido deve devolver False sem lançar excepção."""
        assert verify_password("senha", "hash_completamente_invalido") is False

    def test_password_com_caracteres_especiais(self):
        """Password com caracteres especiais deve funcionar correctamente."""
        password = "P@$$w0rd!#€"
        hash_gerado = hash_password(password)
        assert verify_password(password, hash_gerado) is True
        assert verify_password("P@$$w0rd!#", hash_gerado) is False

    def test_password_case_sensitive(self):
        """A verificação deve ser sensível a maiúsculas/minúsculas."""
        hash_gerado = hash_password("Senha123")
        assert verify_password("senha123", hash_gerado) is False
        assert verify_password("SENHA123", hash_gerado) is False
        assert verify_password("Senha123", hash_gerado) is True
