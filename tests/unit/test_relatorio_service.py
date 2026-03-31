"""
Testes unitários para RelatorioService.

Verificam que os PDFs são gerados sem erros, que os bytes resultantes
formam um PDF válido e que o método ``guardar`` escreve o ficheiro
correctamente.  Não testam o layout visual (isso seria frágil).
"""

import os
import tempfile

import pytest

from src.models.produto import Produto
from src.services.relatorio_service import RelatorioService


# ======================================================================
# Fixtures
# ======================================================================

@pytest.fixture
def svc() -> RelatorioService:
    return RelatorioService()


@pytest.fixture
def vendas_exemplo() -> list[dict]:
    return [
        {"id_venda": 1, "nome": "Ana Costa", "data": "2026-01-10 14:30", "total": 59.90},
        {"id_venda": 2, "nome": "João Silva", "data": "2026-01-11 09:00", "total": 120.00},
        {"id_venda": 3, "nome": "Maria Fernandes", "data": "2026-01-12 16:45", "total": 34.50},
    ]


@pytest.fixture
def produtos_exemplo() -> list[Produto]:
    return [
        Produto(id_produto=1, nome="Teclado Mecânico", preco=79.99, stock=15),
        Produto(id_produto=2, nome="Rato Sem Fios",    preco=29.99, stock=2),
        Produto(id_produto=3, nome="Monitor 27\"",     preco=299.99, stock=0),
        Produto(id_produto=4, nome="Cabo USB-C",       preco=9.99,  stock=50),
    ]


# ======================================================================
# relatorio_vendas
# ======================================================================

class TestRelatorioVendas:
    def test_retorna_bytes(self, svc, vendas_exemplo):
        resultado = svc.relatorio_vendas(vendas_exemplo)
        assert isinstance(resultado, bytes)

    def test_bytes_nao_vazios(self, svc, vendas_exemplo):
        resultado = svc.relatorio_vendas(vendas_exemplo)
        assert len(resultado) > 0

    def test_cabecalho_pdf_valido(self, svc, vendas_exemplo):
        resultado = svc.relatorio_vendas(vendas_exemplo)
        # Todos os PDFs válidos iniciam com a assinatura %PDF
        assert resultado[:4] == b"%PDF"

    def test_lista_vazia_gera_pdf(self, svc):
        resultado = svc.relatorio_vendas([])
        assert isinstance(resultado, bytes)
        assert resultado[:4] == b"%PDF"

    def test_venda_com_campos_em_falta_nao_levanta(self, svc):
        # Campos opcionais devem ter valor padrão
        vendas = [{"id_venda": None, "nome": None, "data": None, "total": None}]
        resultado = svc.relatorio_vendas(vendas)
        assert isinstance(resultado, bytes)

    def test_pdf_maior_com_mais_registos(self, svc, vendas_exemplo):
        pdf_pequeno = svc.relatorio_vendas(vendas_exemplo[:1])
        pdf_grande = svc.relatorio_vendas(vendas_exemplo * 20)
        assert len(pdf_grande) >= len(pdf_pequeno)


# ======================================================================
# relatorio_stock
# ======================================================================

class TestRelatorioStock:
    def test_retorna_bytes(self, svc, produtos_exemplo):
        resultado = svc.relatorio_stock(produtos_exemplo)
        assert isinstance(resultado, bytes)

    def test_bytes_nao_vazios(self, svc, produtos_exemplo):
        resultado = svc.relatorio_stock(produtos_exemplo)
        assert len(resultado) > 0

    def test_cabecalho_pdf_valido(self, svc, produtos_exemplo):
        resultado = svc.relatorio_stock(produtos_exemplo)
        assert resultado[:4] == b"%PDF"

    def test_lista_vazia_gera_pdf(self, svc):
        resultado = svc.relatorio_stock([])
        assert isinstance(resultado, bytes)
        assert resultado[:4] == b"%PDF"

    def test_limiar_personalizado_aceite(self, svc, produtos_exemplo):
        resultado = svc.relatorio_stock(produtos_exemplo, limiar=20)
        assert isinstance(resultado, bytes)

    def test_produto_sem_stock_none_nao_levanta(self, svc):
        produtos = [Produto(id_produto=1, nome="Sem stock", preco=5.0, stock=None)]
        resultado = svc.relatorio_stock(produtos)
        assert isinstance(resultado, bytes)

    def test_produto_sem_preco_none_nao_levanta(self, svc):
        produtos = [Produto(id_produto=1, nome="Sem preco", preco=None, stock=10)]
        resultado = svc.relatorio_stock(produtos)
        assert isinstance(resultado, bytes)


# ======================================================================
# guardar
# ======================================================================

class TestGuardar:
    def test_cria_ficheiro(self, svc, vendas_exemplo):
        conteudo = svc.relatorio_vendas(vendas_exemplo)
        with tempfile.TemporaryDirectory() as tmpdir:
            caminho = os.path.join(tmpdir, "test_vendas.pdf")
            svc.guardar(conteudo, caminho)
            assert os.path.exists(caminho)

    def test_conteudo_igual(self, svc, vendas_exemplo):
        conteudo = svc.relatorio_vendas(vendas_exemplo)
        with tempfile.TemporaryDirectory() as tmpdir:
            caminho = os.path.join(tmpdir, "test.pdf")
            svc.guardar(conteudo, caminho)
            with open(caminho, "rb") as fh:
                lido = fh.read()
            assert lido == conteudo

    def test_cria_diretorios_intermedios(self, svc, vendas_exemplo):
        conteudo = svc.relatorio_vendas(vendas_exemplo)
        with tempfile.TemporaryDirectory() as tmpdir:
            caminho = os.path.join(tmpdir, "subdir", "outro", "relatorio.pdf")
            svc.guardar(conteudo, caminho)
            assert os.path.exists(caminho)

    def test_erro_ao_guardar_em_caminho_invalido(self, svc, vendas_exemplo):
        conteudo = svc.relatorio_vendas(vendas_exemplo)
        # Tentar gravar num ficheiro cujo pai é outro ficheiro (impossível)
        with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
            caminho_invalido = os.path.join(tmp.name, "impossivel.pdf")
            with pytest.raises(OSError):
                svc.guardar(conteudo, caminho_invalido)
