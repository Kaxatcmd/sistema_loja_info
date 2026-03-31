"""
Testes Unitários — Novos Modelos (Melhoria 6)

Cobre:
  - ``Cupao``     — criação, from_dict, to_dict, __repr__, esta_valido,
                    calcular_desconto
  - ``Avaliacao`` — criação, from_dict, to_dict, __repr__
  - ``Wishlist``  — criação, from_dict, to_dict, __repr__
"""

from datetime import date, timedelta

import pytest

from src.models.cupao import Cupao
from src.models.avaliacao import Avaliacao
from src.models.wishlist import Wishlist


# ======================================================================
# Modelo Cupao
# ======================================================================

class TestCupao:
    """Testes para o modelo ``Cupao``."""

    # ------------------------------------------------------------------
    # Criação
    # ------------------------------------------------------------------

    def test_criacao_com_todos_os_campos(self):
        """Instância deve armazenar todos os campos correctamente."""
        validade = date(2027, 12, 31)
        cupao = Cupao(
            id_cupao=1,
            codigo="DESCONTO10",
            desconto=10.0,
            tipo="percentagem",
            ativo=True,
            data_validade=validade,
        )
        assert cupao.id_cupao == 1
        assert cupao.codigo == "DESCONTO10"
        assert cupao.desconto == 10.0
        assert cupao.tipo == "percentagem"
        assert cupao.ativo is True
        assert cupao.data_validade == validade

    def test_criacao_valores_padrao(self):
        """Instância sem argumentos deve usar valores por omissão."""
        cupao = Cupao()
        assert cupao.id_cupao is None
        assert cupao.codigo is None
        assert cupao.tipo == "percentagem"
        assert cupao.ativo is True

    def test_criacao_tipo_fixo(self):
        """Deve suportar tipo 'fixo'."""
        cupao = Cupao(codigo="FIXO5", desconto=5.0, tipo="fixo")
        assert cupao.tipo == "fixo"

    # ------------------------------------------------------------------
    # from_dict
    # ------------------------------------------------------------------

    def test_from_dict_completo(self):
        """``from_dict`` deve mapear correctamente todos os campos."""
        dados = {
            "id_cupao": 3,
            "codigo": "VERAO20",
            "desconto": 20.0,
            "tipo": "percentagem",
            "ativo": True,
            "data_validade": "2027-08-31",
            "data_criacao": "2026-01-01",
        }
        cupao = Cupao.from_dict(dados)
        assert cupao.id_cupao == 3
        assert cupao.codigo == "VERAO20"
        assert cupao.desconto == 20.0
        assert cupao.ativo is True

    def test_from_dict_vazio(self):
        """``from_dict`` vazio deve criar instância com valores por omissão."""
        cupao = Cupao.from_dict({})
        assert cupao.id_cupao is None
        assert cupao.tipo == "percentagem"
        assert cupao.ativo is True

    def test_from_dict_ativo_false(self):
        """``from_dict`` deve converter correctamente ativo=False."""
        cupao = Cupao.from_dict({"ativo": False})
        assert cupao.ativo is False

    def test_from_dict_ativo_zero(self):
        """SQLite armazena booleans como 0/1; deve converter para False."""
        cupao = Cupao.from_dict({"ativo": 0})
        assert cupao.ativo is False

    # ------------------------------------------------------------------
    # to_dict
    # ------------------------------------------------------------------

    def test_to_dict_devolve_dicionario(self):
        """``to_dict`` deve devolver um dicionário com todos os campos."""
        cupao = Cupao(id_cupao=1, codigo="X10", desconto=10.0, tipo="percentagem")
        resultado = cupao.to_dict()
        assert isinstance(resultado, dict)
        assert resultado["id_cupao"] == 1
        assert resultado["codigo"] == "X10"
        assert resultado["desconto"] == 10.0
        assert resultado["tipo"] == "percentagem"

    def test_to_dict_data_validade_isoformat(self):
        """``to_dict`` deve serializar data_validade para string ISO."""
        cupao = Cupao(codigo="ISO", desconto=5.0, data_validade=date(2027, 6, 30))
        resultado = cupao.to_dict()
        assert resultado["data_validade"] == "2027-06-30"

    def test_to_dict_data_validade_none(self):
        """Se data_validade for None, deve permanecer None no dicionário."""
        cupao = Cupao(codigo="SEM_DATA", desconto=5.0)
        assert cupao.to_dict()["data_validade"] is None

    # ------------------------------------------------------------------
    # __repr__
    # ------------------------------------------------------------------

    def test_repr_e_string(self):
        """``__repr__`` deve devolver uma string."""
        assert isinstance(repr(Cupao()), str)

    def test_repr_contem_campos_chave(self):
        """``__repr__`` deve incluir codigo, desconto, tipo e ativo."""
        cupao = Cupao(id_cupao=2, codigo="ABC", desconto=15.0, tipo="fixo", ativo=False)
        r = repr(cupao)
        assert "2" in r
        assert "ABC" in r
        assert "15.0" in r
        assert "fixo" in r
        assert "False" in r

    # ------------------------------------------------------------------
    # esta_valido
    # ------------------------------------------------------------------

    def test_esta_valido_ativo_sem_validade(self):
        """Cupão activo sem data de validade deve ser sempre válido."""
        cupao = Cupao(ativo=True, data_validade=None)
        assert cupao.esta_valido() is True

    def test_esta_valido_inativo(self):
        """Cupão inactivo não deve ser válido independentemente da data."""
        cupao = Cupao(ativo=False, data_validade=date(2099, 1, 1))
        assert cupao.esta_valido() is False

    def test_esta_valido_data_futura(self):
        """Cupão com validade no futuro deve ser válido."""
        cupao = Cupao(ativo=True, data_validade=date.today() + timedelta(days=30))
        assert cupao.esta_valido() is True

    def test_esta_valido_data_passada(self):
        """Cupão com validade no passado deve ser inválido."""
        cupao = Cupao(ativo=True, data_validade=date(2020, 1, 1))
        assert cupao.esta_valido() is False

    def test_esta_valido_hoje(self):
        """Cupão que vence hoje (inclusive) deve ser válido."""
        cupao = Cupao(ativo=True, data_validade=date.today())
        assert cupao.esta_valido() is True

    # ------------------------------------------------------------------
    # calcular_desconto
    # ------------------------------------------------------------------

    def test_calcular_desconto_percentagem(self):
        """Desconto percentual deve ser calculado correctamente."""
        cupao = Cupao(desconto=10.0, tipo="percentagem")
        assert cupao.calcular_desconto(200.0) == pytest.approx(20.0)

    def test_calcular_desconto_fixo(self):
        """Desconto fixo deve ser o valor exacto."""
        cupao = Cupao(desconto=15.0, tipo="fixo")
        assert cupao.calcular_desconto(100.0) == pytest.approx(15.0)

    def test_calcular_desconto_fixo_nao_excede_total(self):
        """Desconto fixo superior ao total deve ser limitado ao total."""
        cupao = Cupao(desconto=200.0, tipo="fixo")
        assert cupao.calcular_desconto(50.0) == pytest.approx(50.0)

    def test_calcular_desconto_sem_valor(self):
        """Sem desconto definido deve devolver 0.0."""
        cupao = Cupao(desconto=None)
        assert cupao.calcular_desconto(100.0) == pytest.approx(0.0)


# ======================================================================
# Modelo Avaliacao
# ======================================================================

class TestAvaliacao:
    """Testes para o modelo ``Avaliacao``."""

    def test_criacao_com_todos_os_campos(self):
        """Instância deve armazenar todos os campos correctamente."""
        av = Avaliacao(
            id_avaliacao=1,
            id_cliente=2,
            id_produto=3,
            nota=5,
            comentario="Excelente produto!",
        )
        assert av.id_avaliacao == 1
        assert av.id_cliente == 2
        assert av.id_produto == 3
        assert av.nota == 5
        assert av.comentario == "Excelente produto!"

    def test_criacao_valores_padrao(self):
        """Instância sem argumentos deve ter campos None."""
        av = Avaliacao()
        assert av.id_avaliacao is None
        assert av.nota is None
        assert av.comentario is None

    def test_from_dict_completo(self):
        """``from_dict`` deve mapear correctamente todos os campos."""
        dados = {
            "id_avaliacao": 7,
            "id_cliente": 1,
            "id_produto": 4,
            "nota": 4,
            "comentario": "Muito bom.",
            "data_criacao": "2026-03-10",
        }
        av = Avaliacao.from_dict(dados)
        assert av.id_avaliacao == 7
        assert av.nota == 4
        assert av.comentario == "Muito bom."
        assert av.data_criacao == "2026-03-10"

    def test_from_dict_vazio(self):
        """``from_dict`` vazio deve criar instância totalmente em None."""
        av = Avaliacao.from_dict({})
        assert av.id_avaliacao is None
        assert av.nota is None

    def test_to_dict_devolve_dicionario(self):
        """``to_dict`` deve devolver dicionário com todos os campos."""
        av = Avaliacao(id_avaliacao=1, id_cliente=2, id_produto=3, nota=3)
        resultado = av.to_dict()
        assert isinstance(resultado, dict)
        assert resultado["id_avaliacao"] == 1
        assert resultado["nota"] == 3

    def test_to_dict_campos_corretos(self):
        """``to_dict`` deve incluir exactamente os campos esperados."""
        av = Avaliacao()
        chaves = set(av.to_dict().keys())
        assert chaves == {
            "id_avaliacao", "id_cliente", "id_produto",
            "nota", "comentario", "data_criacao",
        }

    def test_repr_e_string(self):
        """``__repr__`` deve devolver uma string."""
        assert isinstance(repr(Avaliacao()), str)

    def test_repr_contem_campos_chave(self):
        """``__repr__`` deve incluir ids e nota."""
        av = Avaliacao(id_avaliacao=1, id_cliente=2, id_produto=3, nota=5)
        r = repr(av)
        assert "1" in r
        assert "2" in r
        assert "3" in r
        assert "5" in r


# ======================================================================
# Modelo Wishlist
# ======================================================================

class TestWishlist:
    """Testes para o modelo ``Wishlist``."""

    def test_criacao_com_todos_os_campos(self):
        """Instância deve armazenar todos os campos correctamente."""
        item = Wishlist(
            id_wishlist=10,
            id_cliente=1,
            id_produto=5,
            data_criacao="2026-03-15",
        )
        assert item.id_wishlist == 10
        assert item.id_cliente == 1
        assert item.id_produto == 5
        assert item.data_criacao == "2026-03-15"

    def test_criacao_valores_padrao(self):
        """Instância sem argumentos deve ter campos None."""
        item = Wishlist()
        assert item.id_wishlist is None
        assert item.id_cliente is None
        assert item.id_produto is None

    def test_from_dict_completo(self):
        """``from_dict`` deve mapear correctamente todos os campos."""
        dados = {
            "id_wishlist": 3,
            "id_cliente": 1,
            "id_produto": 2,
            "data_criacao": "2026-02-20",
        }
        item = Wishlist.from_dict(dados)
        assert item.id_wishlist == 3
        assert item.id_cliente == 1
        assert item.id_produto == 2

    def test_from_dict_vazio(self):
        """``from_dict`` vazio deve criar instância totalmente em None."""
        item = Wishlist.from_dict({})
        assert item.id_wishlist is None
        assert item.id_cliente is None

    def test_to_dict_devolve_dicionario(self):
        """``to_dict`` deve devolver dicionário com todos os campos."""
        item = Wishlist(id_wishlist=1, id_cliente=2, id_produto=3)
        resultado = item.to_dict()
        assert isinstance(resultado, dict)
        assert resultado["id_wishlist"] == 1
        assert resultado["id_cliente"] == 2
        assert resultado["id_produto"] == 3

    def test_to_dict_campos_corretos(self):
        """``to_dict`` deve incluir exactamente os campos esperados."""
        item = Wishlist()
        chaves = set(item.to_dict().keys())
        assert chaves == {"id_wishlist", "id_cliente", "id_produto", "data_criacao"}

    def test_repr_e_string(self):
        """``__repr__`` deve devolver uma string."""
        assert isinstance(repr(Wishlist()), str)

    def test_repr_contem_campos_chave(self):
        """``__repr__`` deve incluir id_wishlist, id_cliente e id_produto."""
        item = Wishlist(id_wishlist=1, id_cliente=2, id_produto=3)
        r = repr(item)
        assert "1" in r
        assert "2" in r
        assert "3" in r
