"""
Testes Unitários — src/utils/validators.py

Cobre todas as funções de validação:
  - validar_email
  - validar_password
  - validar_preco
  - validar_stock
  - validar_nome_produto
"""

import pytest
from src.utils.validators import (
    validar_email,
    validar_password,
    validar_preco,
    validar_stock,
    validar_nome_produto,
)


# ======================================================================
# validar_email
# ======================================================================

class TestValidarEmail:
    """Testes para a função ``validar_email``."""

    def test_email_valido(self):
        """Email com formato correcto deve ser aceite."""
        valido, msg = validar_email("utilizador@exemplo.pt")
        assert valido is True
        assert msg == "OK"

    def test_email_valido_subdominio(self):
        """Email com subdomínio deve ser aceite."""
        valido, _ = validar_email("a@b.co.uk")
        assert valido is True

    def test_email_valido_com_ponto_no_nome(self):
        """Email com ponto no utilizador deve ser aceite."""
        valido, _ = validar_email("nome.apelido@empresa.com")
        assert valido is True

    def test_email_valido_com_espacos_nas_extremidades(self):
        """Espaços em branco nas extremidades devem ser ignorados."""
        valido, _ = validar_email("  user@test.com  ")
        assert valido is True

    def test_email_vazio(self):
        """String vazia deve ser rejeitada."""
        valido, msg = validar_email("")
        assert valido is False
        assert "obrigatório" in msg.lower()

    def test_email_apenas_espacos(self):
        """String com apenas espaços deve ser tratada como vazia."""
        valido, _ = validar_email("   ")
        assert valido is False

    def test_email_sem_arroba(self):
        """Email sem @ deve ser rejeitado."""
        valido, msg = validar_email("sem-arroba.com")
        assert valido is False
        assert "inválido" in msg.lower()

    def test_email_sem_dominio(self):
        """Email sem domínio deve ser rejeitado."""
        valido, _ = validar_email("user@")
        assert valido is False

    def test_email_sem_extensao(self):
        """Email sem extensão de domínio deve ser rejeitado."""
        valido, _ = validar_email("user@dominio")
        assert valido is False

    def test_email_com_espacos_internos(self):
        """Email com espaços internos deve ser rejeitado."""
        valido, _ = validar_email("user @domain.com")
        assert valido is False


# ======================================================================
# validar_password
# ======================================================================

class TestValidarPassword:
    """Testes para a função ``validar_password``."""

    def test_password_valida(self):
        """Password com 6 ou mais caracteres deve ser aceite."""
        valido, msg = validar_password("abc123")
        assert valido is True
        assert msg == "OK"

    def test_password_longa_valida(self):
        """Password longa deve ser aceite."""
        valido, _ = validar_password("P@ssw0rd_Segura_2026!")
        assert valido is True

    def test_password_vazia(self):
        """Password vazia deve ser rejeitada."""
        valido, msg = validar_password("")
        assert valido is False
        assert "obrigatória" in msg.lower()

    def test_password_curta(self):
        """Password com menos de 6 caracteres deve ser rejeitada."""
        valido, msg = validar_password("abc")
        assert valido is False
        assert "6" in msg  # deve mencionar o mínimo

    def test_password_exatamente_minimo(self):
        """Password com exactamente 6 caracteres deve ser aceite."""
        valido, _ = validar_password("123456")
        assert valido is True

    def test_password_cinco_caracteres(self):
        """Password com 5 caracteres deve ser rejeitada."""
        valido, _ = validar_password("12345")
        assert valido is False


# ======================================================================
# validar_preco
# ======================================================================

class TestValidarPreco:
    """Testes para a função ``validar_preco``."""

    def test_preco_valido_inteiro(self):
        """Preço inteiro como string deve ser aceite."""
        valido, preco, msg = validar_preco("100")
        assert valido is True
        assert preco == 100.0
        assert msg == "OK"

    def test_preco_valido_decimal_ponto(self):
        """Preço decimal com ponto deve ser aceite."""
        valido, preco, _ = validar_preco("49.99")
        assert valido is True
        assert preco == pytest.approx(49.99)

    def test_preco_valido_decimal_virgula(self):
        """Preço decimal com vírgula (formato PT) deve ser aceite."""
        valido, preco, _ = validar_preco("49,99")
        assert valido is True
        assert preco == pytest.approx(49.99)

    def test_preco_zero(self):
        """Preço zero deve ser aceite (produto gratuito)."""
        valido, preco, _ = validar_preco("0")
        assert valido is True
        assert preco == 0.0

    def test_preco_vazio(self):
        """String vazia deve ser rejeitada."""
        valido, preco, msg = validar_preco("")
        assert valido is False
        assert preco is None
        assert "obrigatório" in msg.lower()

    def test_preco_negativo(self):
        """Preço negativo deve ser rejeitado."""
        valido, preco, msg = validar_preco("-5.00")
        assert valido is False
        assert preco is None
        assert "negativo" in msg.lower()

    def test_preco_texto(self):
        """Texto não numérico deve ser rejeitado."""
        valido, preco, msg = validar_preco("abc")
        assert valido is False
        assert preco is None
        assert "inválido" in msg.lower()


# ======================================================================
# validar_stock
# ======================================================================

class TestValidarStock:
    """Testes para a função ``validar_stock``."""

    def test_stock_valido(self):
        """Stock inteiro positivo deve ser aceite."""
        valido, stock, msg = validar_stock("10")
        assert valido is True
        assert stock == 10
        assert msg == "OK"

    def test_stock_zero(self):
        """Stock zero deve ser aceite."""
        valido, stock, _ = validar_stock("0")
        assert valido is True
        assert stock == 0

    def test_stock_vazio(self):
        """String vazia deve ser rejeitada."""
        valido, stock, msg = validar_stock("")
        assert valido is False
        assert stock is None
        assert "obrigatório" in msg.lower()

    def test_stock_negativo(self):
        """Stock negativo deve ser rejeitado."""
        valido, stock, msg = validar_stock("-1")
        assert valido is False
        assert stock is None
        assert "negativo" in msg.lower()

    def test_stock_decimal(self):
        """Stock decimal (não inteiro) deve ser rejeitado."""
        valido, stock, msg = validar_stock("3.5")
        assert valido is False
        assert stock is None
        assert "inválido" in msg.lower()

    def test_stock_texto(self):
        """Texto não numérico deve ser rejeitado."""
        valido, stock, msg = validar_stock("dez")
        assert valido is False
        assert stock is None


# ======================================================================
# validar_nome_produto
# ======================================================================

class TestValidarNomeProduto:
    """Testes para a função ``validar_nome_produto``."""

    def test_nome_valido(self):
        """Nome curto e simples deve ser aceite."""
        valido, msg = validar_nome_produto("Rato Óptico")
        assert valido is True
        assert msg == "OK"

    def test_nome_vazio(self):
        """Nome vazio deve ser rejeitado."""
        valido, msg = validar_nome_produto("")
        assert valido is False

    def test_nome_muito_longo(self):
        """Nome com mais de 100 caracteres deve ser rejeitado."""
        nome_longo = "A" * 101
        valido, msg = validar_nome_produto(nome_longo)
        assert valido is False

    def test_nome_no_limite(self):
        """Nome com exactamente 100 caracteres deve ser aceite."""
        nome_limite = "B" * 100
        valido, _ = validar_nome_produto(nome_limite)
        assert valido is True
