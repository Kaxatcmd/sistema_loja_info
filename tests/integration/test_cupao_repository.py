"""
Testes de Integração — CupaoRepository

Usa a fixture ``bd_memoria`` (SQLite in-memory) do conftest.py.
Cobre: criar, listar_todos, listar_ativos, buscar_por_id,
       buscar_por_codigo, validar_cupao, atualizar, desativar, deletar.
"""

import pytest
from datetime import date, timedelta

from src.repositories.cupao_repository import CupaoRepository
from src.models.cupao import Cupao


# ======================================================================
# Helpers
# ======================================================================

def _inserir_cupao(bd, codigo="DESC10", desconto=10.0, tipo="percentagem",
                   ativo=True, data_validade=None):
    """Insere um cupão directamente na BD e devolve o ID gerado."""
    return bd.executar_update(
        "INSERT INTO cupoes (codigo, desconto, tipo, ativo, data_validade) "
        "VALUES (?, ?, ?, ?, ?)",
        (codigo.upper(), desconto, tipo, int(ativo), data_validade),
    )


# ======================================================================
# TestCupaoRepository
# ======================================================================

class TestCupaoRepository:

    # ------------------------------------------------------------------
    # listar_todos
    # ------------------------------------------------------------------

    def test_listar_todos_bd_vazia(self, bd_memoria):
        repo = CupaoRepository(bd_memoria)
        assert repo.listar_todos() == []

    def test_listar_todos_devolve_todos(self, bd_memoria):
        _inserir_cupao(bd_memoria, "A10")
        _inserir_cupao(bd_memoria, "B20")
        repo = CupaoRepository(bd_memoria)
        assert len(repo.listar_todos()) == 2

    def test_listar_todos_ordem_alfabetica(self, bd_memoria):
        _inserir_cupao(bd_memoria, "ZEBRA")
        _inserir_cupao(bd_memoria, "ANFORA")
        repo = CupaoRepository(bd_memoria)
        codigos = [c.codigo for c in repo.listar_todos()]
        assert codigos == sorted(codigos)

    def test_listar_todos_devolve_instancias_cupao(self, bd_memoria):
        _inserir_cupao(bd_memoria, "TEST1")
        repo = CupaoRepository(bd_memoria)
        for item in repo.listar_todos():
            assert isinstance(item, Cupao)

    # ------------------------------------------------------------------
    # listar_ativos
    # ------------------------------------------------------------------

    def test_listar_ativos_exclui_inativos(self, bd_memoria):
        _inserir_cupao(bd_memoria, "ATIVO1", ativo=True)
        _inserir_cupao(bd_memoria, "INATIVO1", ativo=False)
        repo = CupaoRepository(bd_memoria)
        ativos = repo.listar_ativos()
        assert len(ativos) == 1
        assert ativos[0].codigo == "ATIVO1"

    def test_listar_ativos_bd_vazia(self, bd_memoria):
        assert CupaoRepository(bd_memoria).listar_ativos() == []

    # ------------------------------------------------------------------
    # buscar_por_id
    # ------------------------------------------------------------------

    def test_buscar_por_id_existente(self, bd_memoria):
        id_ = _inserir_cupao(bd_memoria, "ID10", desconto=10.0)
        repo = CupaoRepository(bd_memoria)
        cupao = repo.buscar_por_id(id_)
        assert cupao is not None
        assert cupao.codigo == "ID10"
        assert cupao.desconto == 10.0

    def test_buscar_por_id_inexistente(self, bd_memoria):
        repo = CupaoRepository(bd_memoria)
        assert repo.buscar_por_id(9999) is None

    # ------------------------------------------------------------------
    # buscar_por_codigo
    # ------------------------------------------------------------------

    def test_buscar_por_codigo_existente(self, bd_memoria):
        _inserir_cupao(bd_memoria, "VERAO", desconto=20.0)
        repo = CupaoRepository(bd_memoria)
        cupao = repo.buscar_por_codigo("verao")   # case-insensitive
        assert cupao is not None
        assert cupao.desconto == 20.0

    def test_buscar_por_codigo_maiusculas_minusculas(self, bd_memoria):
        _inserir_cupao(bd_memoria, "NATAL")
        repo = CupaoRepository(bd_memoria)
        assert repo.buscar_por_codigo("natal") is not None
        assert repo.buscar_por_codigo("NaTaL") is not None

    def test_buscar_por_codigo_inexistente(self, bd_memoria):
        repo = CupaoRepository(bd_memoria)
        assert repo.buscar_por_codigo("inexistente") is None

    # ------------------------------------------------------------------
    # validar_cupao
    # ------------------------------------------------------------------

    def test_validar_cupao_valido(self, bd_memoria):
        _inserir_cupao(bd_memoria, "VALIDO", ativo=True,
                       data_validade=str(date.today() + timedelta(days=30)))
        repo = CupaoRepository(bd_memoria)
        valido, cupao, msg = repo.validar_cupao("VALIDO")
        assert valido is True
        assert cupao is not None
        assert "válido" in msg.lower()

    def test_validar_cupao_inexistente(self, bd_memoria):
        repo = CupaoRepository(bd_memoria)
        valido, cupao, msg = repo.validar_cupao("NAOEXISTE")
        assert valido is False
        assert cupao is None

    def test_validar_cupao_inativo(self, bd_memoria):
        _inserir_cupao(bd_memoria, "INATIVO", ativo=False)
        repo = CupaoRepository(bd_memoria)
        valido, cupao, msg = repo.validar_cupao("INATIVO")
        assert valido is False
        assert cupao is None

    def test_validar_cupao_expirado(self, bd_memoria):
        _inserir_cupao(bd_memoria, "EXPIRADO", ativo=True,
                       data_validade="2020-01-01")
        repo = CupaoRepository(bd_memoria)
        valido, cupao, msg = repo.validar_cupao("EXPIRADO")
        assert valido is False
        assert cupao is None

    def test_validar_cupao_sem_data_validade(self, bd_memoria):
        """Cupão activo sem data de validade deve ser sempre válido."""
        _inserir_cupao(bd_memoria, "SEMDATA", ativo=True, data_validade=None)
        repo = CupaoRepository(bd_memoria)
        valido, cupao, msg = repo.validar_cupao("SEMDATA")
        assert valido is True
        assert cupao is not None

    # ------------------------------------------------------------------
    # criar
    # ------------------------------------------------------------------

    def test_criar_devolve_id(self, bd_memoria):
        repo = CupaoRepository(bd_memoria)
        novo = Cupao(codigo="NOVO10", desconto=10.0, tipo="percentagem")
        resultado = repo.criar(novo)
        assert resultado.id_cupao is not None
        assert resultado.id_cupao > 0

    def test_criar_persiste_na_bd(self, bd_memoria):
        repo = CupaoRepository(bd_memoria)
        repo.criar(Cupao(codigo="persist", desconto=5.0, tipo="fixo"))
        encontrado = repo.buscar_por_codigo("PERSIST")
        assert encontrado is not None
        assert encontrado.tipo == "fixo"

    def test_criar_normaliza_codigo_maiusculas(self, bd_memoria):
        """O código deve ser armazenado em maiúsculas."""
        repo = CupaoRepository(bd_memoria)
        repo.criar(Cupao(codigo="minusculo", desconto=10.0))
        encontrado = repo.buscar_por_codigo("MINUSCULO")
        assert encontrado is not None
        assert encontrado.codigo == "MINUSCULO"

    def test_criar_multiplos_ids_unicos(self, bd_memoria):
        repo = CupaoRepository(bd_memoria)
        c1 = repo.criar(Cupao(codigo="C1", desconto=5.0))
        c2 = repo.criar(Cupao(codigo="C2", desconto=10.0))
        assert c1.id_cupao != c2.id_cupao

    # ------------------------------------------------------------------
    # atualizar
    # ------------------------------------------------------------------

    def test_atualizar_cupao(self, bd_memoria):
        id_ = _inserir_cupao(bd_memoria, "ANTIGO", desconto=5.0)
        repo = CupaoRepository(bd_memoria)
        cupao = repo.buscar_por_id(id_)
        cupao.codigo = "NOVO"
        cupao.desconto = 15.0
        repo.atualizar(cupao)
        actualizado = repo.buscar_por_id(id_)
        assert actualizado.codigo == "NOVO"
        assert actualizado.desconto == 15.0

    def test_atualizar_sem_id_lanca_valueerror(self, bd_memoria):
        repo = CupaoRepository(bd_memoria)
        cupao_sem_id = Cupao(codigo="SEM", desconto=5.0)
        with pytest.raises(ValueError, match="id_cupao"):
            repo.atualizar(cupao_sem_id)

    # ------------------------------------------------------------------
    # desativar
    # ------------------------------------------------------------------

    def test_desativar_cupao(self, bd_memoria):
        id_ = _inserir_cupao(bd_memoria, "DESACT", ativo=True)
        repo = CupaoRepository(bd_memoria)
        repo.desativar(id_)
        cupao = repo.buscar_por_id(id_)
        assert bool(cupao.ativo) is False

    def test_desativar_nao_remove_da_bd(self, bd_memoria):
        id_ = _inserir_cupao(bd_memoria, "MANTEM", ativo=True)
        repo = CupaoRepository(bd_memoria)
        repo.desativar(id_)
        assert repo.buscar_por_id(id_) is not None

    # ------------------------------------------------------------------
    # deletar
    # ------------------------------------------------------------------

    def test_deletar_cupao(self, bd_memoria):
        id_ = _inserir_cupao(bd_memoria, "DELETAR")
        repo = CupaoRepository(bd_memoria)
        repo.deletar(id_)
        assert repo.buscar_por_id(id_) is None

    def test_deletar_nao_afeta_outros(self, bd_memoria):
        id1 = _inserir_cupao(bd_memoria, "MANTER")
        id2 = _inserir_cupao(bd_memoria, "REMOVER2")
        repo = CupaoRepository(bd_memoria)
        repo.deletar(id2)
        assert repo.buscar_por_id(id1) is not None
