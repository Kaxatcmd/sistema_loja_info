"""
Testes unitários para StockService.

Verificam a lógica de detecção de stock baixo, formatação de alertas
e o resumo textual, utilizando a BD SQLite in-memory partilhada.
"""

import pytest

from src.services.stock_service import StockService


# ======================================================================
# Helpers
# ======================================================================

def _inserir_produto(bd, nome: str, preco: float, stock: int) -> int:
    """Insere um produto na BD e devolve o id gerado."""
    return bd.executar_update(
        "INSERT INTO produtos (nome, preco, stock) VALUES (%s, %s, %s)",
        (nome, preco, stock),
    )


# ======================================================================
# Inicialização
# ======================================================================

class TestStockServiceInit:
    def test_limiar_padrao_valido(self, bd_memoria):
        svc = StockService(bd_memoria)
        assert svc.limiar >= 0

    def test_limiar_personalizado(self, bd_memoria):
        svc = StockService(bd_memoria, limiar=10)
        assert svc.limiar == 10

    def test_limiar_zero_permitido(self, bd_memoria):
        svc = StockService(bd_memoria, limiar=0)
        assert svc.limiar == 0

    def test_limiar_negativo_levanta_valor_error(self, bd_memoria):
        with pytest.raises(ValueError, match="limiar"):
            StockService(bd_memoria, limiar=-1)


# ======================================================================
# produtos_stock_baixo
# ======================================================================

class TestProdutosStockBaixo:
    def test_bd_vazia_retorna_lista_vazia(self, bd_memoria):
        svc = StockService(bd_memoria, limiar=5)
        assert svc.produtos_stock_baixo() == []

    def test_produto_acima_limiar_nao_aparece(self, bd_memoria):
        _inserir_produto(bd_memoria, "Monitor", 299.99, 10)
        svc = StockService(bd_memoria, limiar=5)
        assert svc.produtos_stock_baixo() == []

    def test_produto_no_limiar_exato_nao_aparece(self, bd_memoria):
        # stock == limiar  → não deve aparecer (só stock < limiar)
        _inserir_produto(bd_memoria, "Rato", 29.99, 5)
        svc = StockService(bd_memoria, limiar=5)
        assert svc.produtos_stock_baixo() == []

    def test_produto_abaixo_limiar_aparece(self, bd_memoria):
        _inserir_produto(bd_memoria, "Cabo USB", 9.99, 2)
        svc = StockService(bd_memoria, limiar=5)
        resultado = svc.produtos_stock_baixo()
        assert len(resultado) == 1
        assert resultado[0].nome == "Cabo USB"
        assert resultado[0].stock == 2

    def test_stock_zero_aparece(self, bd_memoria):
        _inserir_produto(bd_memoria, "Adaptador", 14.99, 0)
        svc = StockService(bd_memoria, limiar=5)
        resultado = svc.produtos_stock_baixo()
        assert len(resultado) == 1
        assert resultado[0].stock == 0

    def test_varios_produtos_ordenados_por_stock_depois_nome(self, bd_memoria):
        _inserir_produto(bd_memoria, "Zebra", 5.0, 3)
        _inserir_produto(bd_memoria, "Alfa",  5.0, 3)
        _inserir_produto(bd_memoria, "Beta",  5.0, 1)
        svc = StockService(bd_memoria, limiar=5)
        resultado = svc.produtos_stock_baixo()
        # stock 1 vem primeiro, depois stock 3 alfabético
        assert resultado[0].nome == "Beta"
        assert resultado[1].nome == "Alfa"
        assert resultado[2].nome == "Zebra"

    def test_apenas_produtos_abaixo_retornados(self, bd_memoria):
        _inserir_produto(bd_memoria, "OK",   10.0, 20)
        _inserir_produto(bd_memoria, "Baixo", 5.0,  1)
        svc = StockService(bd_memoria, limiar=5)
        resultado = svc.produtos_stock_baixo()
        assert len(resultado) == 1
        assert resultado[0].nome == "Baixo"


# ======================================================================
# obter_alertas
# ======================================================================

class TestObterAlertas:
    def test_sem_problemas_retorna_lista_vazia(self, bd_memoria):
        svc = StockService(bd_memoria, limiar=5)
        assert svc.obter_alertas() == []

    def test_formato_mensagem_alerta(self, bd_memoria):
        _inserir_produto(bd_memoria, "Pen USB", 12.0, 2)
        svc = StockService(bd_memoria, limiar=5)
        alertas = svc.obter_alertas()
        assert len(alertas) == 1
        # Deve conter o nome do produto e o stock actual
        assert "Pen USB" in alertas[0]
        assert "2" in alertas[0]
        # Deve indicar o limiar mínimo
        assert "5" in alertas[0]

    def test_multiplos_alertas(self, bd_memoria):
        _inserir_produto(bd_memoria, "A", 1.0, 0)
        _inserir_produto(bd_memoria, "B", 2.0, 3)
        svc = StockService(bd_memoria, limiar=5)
        alertas = svc.obter_alertas()
        assert len(alertas) == 2


# ======================================================================
# tem_alertas
# ======================================================================

class TestTemAlertas:
    def test_sem_produtos_retorna_false(self, bd_memoria):
        svc = StockService(bd_memoria, limiar=5)
        assert svc.tem_alertas() is False

    def test_produto_acima_retorna_false(self, bd_memoria):
        _inserir_produto(bd_memoria, "OK", 5.0, 100)
        svc = StockService(bd_memoria, limiar=5)
        assert svc.tem_alertas() is False

    def test_produto_abaixo_retorna_true(self, bd_memoria):
        _inserir_produto(bd_memoria, "Baixo", 5.0, 1)
        svc = StockService(bd_memoria, limiar=5)
        assert svc.tem_alertas() is True

    def test_produto_no_limiar_exato_retorna_false(self, bd_memoria):
        _inserir_produto(bd_memoria, "Exato", 5.0, 5)
        svc = StockService(bd_medicina := bd_memoria, limiar=5)
        assert svc.tem_alertas() is False


# ======================================================================
# resumo
# ======================================================================

class TestResumo:
    def test_sem_alertas_retorna_string_vazia(self, bd_memoria):
        svc = StockService(bd_memoria, limiar=5)
        assert svc.resumo() == ""

    def test_um_produto_formato_correto(self, bd_memoria):
        _inserir_produto(bd_memoria, "Cable", 3.0, 1)
        svc = StockService(bd_memoria, limiar=5)
        res = svc.resumo()
        assert res != ""
        assert "1" in res  # contagem de produto(s)
        assert "5" in res  # limiar

    def test_varios_produtos_contagem_correta(self, bd_memoria):
        _inserir_produto(bd_memoria, "A", 1.0, 0)
        _inserir_produto(bd_memoria, "B", 2.0, 2)
        _inserir_produto(bd_memoria, "C", 3.0, 4)  # stock < 5 → conta
        svc = StockService(bd_memoria, limiar=5)
        res = svc.resumo()
        assert "3" in res

    def test_limiar_personalizado_refletido(self, bd_memoria):
        _inserir_produto(bd_memoria, "X", 1.0, 3)
        svc = StockService(bd_memoria, limiar=10)
        res = svc.resumo()
        assert "10" in res
