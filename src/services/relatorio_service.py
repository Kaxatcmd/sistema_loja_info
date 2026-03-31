"""
Serviço de Geração de Relatórios PDF.

Responsabilidades:
  - Gerar um relatório de vendas (histórico) em formato PDF.
  - Gerar um relatório de stock/inventário em formato PDF.
  - Devolver os bytes do PDF ou guardá-lo em disco.

O módulo não tem qualquer dependência de Tkinter e pode ser instanciado
e testado de forma isolada.

Dependência externa: fpdf2 (``pip install fpdf2``).
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Sequence

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from src.config import STOCK_MINIMO
from src.models.produto import Produto
from src.utils.logger import obter_logger

logger = obter_logger(__name__)

# ---------------------------------------------------------------------------
# Constantes de formatação
# ---------------------------------------------------------------------------

_AZUL_PRIMARIO = (30, 64, 175)
_CINZA_CABECALHO = (240, 244, 248)
_LARANJA_ALERTA_FUNDO = (255, 237, 213)
_BRANCO = (255, 255, 255)

# Caminhos candidatos para fonte DejaVuSans (Unicode) no sistema
_DEJAVU_CANDIDATES = [
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
     "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ("/usr/share/fonts/dejavu/DejaVuSans.ttf",
     "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"),
]


def _encontrar_dejavu() -> tuple[str, str] | None:
    """Devolve (regular, bold) se DejaVuSans TTF existir no sistema."""
    for regular, bold in _DEJAVU_CANDIDATES:
        if os.path.exists(regular) and os.path.exists(bold):
            return regular, bold
    return None


# ---------------------------------------------------------------------------
# Classe principal
# ---------------------------------------------------------------------------

class RelatorioService:
    """
    Gera relatórios PDF para o painel de administração.

    Todos os métodos ``relatorio_*`` devolvem ``bytes`` (o conteúdo do
    ficheiro PDF).  Use :meth:`guardar` para persistir em disco.

    Exemplo::

        svc = RelatorioService()
        pdf_bytes = svc.relatorio_vendas(vendas)
        svc.guardar(pdf_bytes, "/tmp/vendas.pdf")
    """

    # ------------------------------------------------------------------
    # Relatório de Vendas
    # ------------------------------------------------------------------

    def relatorio_vendas(self, vendas: Sequence[dict]) -> bytes:
        """
        Gera um PDF com o histórico de vendas.

        Args:
            vendas: Sequência de dicionários com as chaves
                    ``id_venda``, ``nome``, ``data`` e ``total``.

        Returns:
            Conteúdo do PDF como ``bytes``.
        """
        pdf, fonte = self._base_pdf("Relatorio de Vendas")

        self._titulo_secao(pdf, fonte, "Historico de Vendas")
        self._data_geracao(pdf, fonte)

        cabecalhos = ["ID", "Cliente", "Data", "Total (EUR)"]
        larguras = [18, 75, 40, 35]
        self._cabecalho_tabela(pdf, fonte, cabecalhos, larguras)

        total_geral = 0.0
        for v in vendas:
            total_geral += float(v.get("total") or 0)
            linha = [
                str(v.get("id_venda") or ""),
                str(v.get("nome") or "")[:35],
                str(v.get("data") or "")[:16],
                f"{float(v.get('total') or 0):.2f}",
            ]
            self._linha_tabela(pdf, fonte, linha, larguras)

        # rodapé de totais
        pdf.set_font(fonte, "B", 10)
        pdf.set_fill_color(*_CINZA_CABECALHO)
        pdf.set_text_color(*_AZUL_PRIMARIO)
        col_totais = sum(larguras[:3])
        pdf.cell(col_totais, 8, "TOTAL GERAL", border=1, fill=True, align="R",
                 new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(larguras[3], 8, f"{total_geral:.2f}", border=1, fill=True, align="R",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        logger.info("PDF de vendas gerado: %d registos, total=%.2f", len(vendas), total_geral)
        return bytes(pdf.output())

    # ------------------------------------------------------------------
    # Relatório de Stock / Inventário
    # ------------------------------------------------------------------

    def relatorio_stock(self, produtos: Sequence[Produto], limiar: int = STOCK_MINIMO) -> bytes:
        """
        Gera um PDF com o inventário de produtos.

        Produtos com ``stock < limiar`` são assinalados com ``[!]`` na
        coluna de estado.

        Args:
            produtos: Sequência de instâncias de :class:`Produto`.
            limiar:   Stock mínimo considerado aceitável.

        Returns:
            Conteúdo do PDF como ``bytes``.
        """
        pdf, fonte = self._base_pdf("Relatorio de Stock")
        self._titulo_secao(pdf, fonte, "Inventario de Produtos")
        self._data_geracao(pdf, fonte)

        pdf.set_font(fonte, "I", 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 6, f"Stock baixo = stock < {limiar} unidades",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(2)

        cabecalhos = ["ID", "Nome", "Preco (EUR)", "Stock", "Estado"]
        larguras = [15, 80, 28, 20, 25]
        self._cabecalho_tabela(pdf, fonte, cabecalhos, larguras)

        em_alerta = 0
        for p in produtos:
            baixo = (p.stock is not None and p.stock < limiar)
            if baixo:
                em_alerta += 1

            estado = "[!] BAIXO" if baixo else "OK"
            linha = [
                str(p.id_produto or ""),
                str(p.nome or "")[:38],
                f"{float(p.preco or 0):.2f}",
                str(p.stock if p.stock is not None else "-"),
                estado,
            ]
            fill_cor = _LARANJA_ALERTA_FUNDO if baixo else _BRANCO
            self._linha_tabela(pdf, fonte, linha, larguras, fill_color=fill_cor)

        pdf.ln(4)
        pdf.set_font(fonte, "B", 10)
        pdf.set_text_color(*_AZUL_PRIMARIO)
        pdf.cell(0, 8,
                 f"Total de produtos: {len(produtos)}    |    Em alerta: {em_alerta}",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        logger.info("PDF de stock gerado: %d produtos, %d em alerta", len(produtos), em_alerta)
        return bytes(pdf.output())

    # ------------------------------------------------------------------
    # Utilitário: guardar em disco
    # ------------------------------------------------------------------

    def guardar(self, conteudo: bytes, caminho: str) -> None:
        """
        Grava o PDF (bytes) no caminho indicado.

        Args:
            conteudo: Bytes gerados por um dos métodos ``relatorio_*``.
            caminho:  Caminho completo do ficheiro de destino.

        Raises:
            OSError: Se não for possível escrever o ficheiro.
        """
        destino = os.path.abspath(caminho)
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        with open(destino, "wb") as fh:
            fh.write(conteudo)
        logger.info("Relatorio guardado em: %s (%d bytes)", destino, len(conteudo))

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    @staticmethod
    def _base_pdf(titulo: str) -> tuple[FPDF, str]:
        """
        Cria documento PDF base e devolve (pdf, nome_fonte).

        Tenta usar DejaVuSans (Unicode) se disponível no sistema;
        caso contrário usa Helvetica (Latin-1).
        """
        pdf = FPDF(orientation="P", unit="mm", format="A4")
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        dejavu = _encontrar_dejavu()
        if dejavu:
            pdf.add_font("DejaVu", "", dejavu[0])
            pdf.add_font("DejaVu", "B", dejavu[1])
            pdf.add_font("DejaVu", "I", dejavu[0])  # itálico → regular como fallback
            fonte = "DejaVu"
        else:
            fonte = "Helvetica"

        # Título principal (faixa azul)
        pdf.set_fill_color(*_AZUL_PRIMARIO)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font(fonte, "B", 16)
        pdf.cell(0, 12, f"  {titulo}", fill=True,
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(4)

        return pdf, fonte

    @staticmethod
    def _titulo_secao(pdf: FPDF, fonte: str, texto: str) -> None:
        pdf.set_font(fonte, "B", 12)
        pdf.set_text_color(*_AZUL_PRIMARIO)
        pdf.cell(0, 8, texto, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    @staticmethod
    def _data_geracao(pdf: FPDF, fonte: str) -> None:
        pdf.set_font(fonte, "I", 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 6, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(3)

    @staticmethod
    def _cabecalho_tabela(pdf: FPDF, fonte: str,
                          cabecalhos: list[str], larguras: list[int]) -> None:
        pdf.set_fill_color(*_AZUL_PRIMARIO)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font(fonte, "B", 10)
        for texto, larg in zip(cabecalhos, larguras):
            pdf.cell(larg, 8, texto, border=1, fill=True, align="C",
                     new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.ln()

    @staticmethod
    def _linha_tabela(
        pdf: FPDF,
        fonte: str,
        valores: list[str],
        larguras: list[int],
        fill_color: tuple[int, int, int] = _BRANCO,
    ) -> None:
        pdf.set_text_color(30, 30, 30)
        pdf.set_font(fonte, size=9)
        pdf.set_fill_color(*fill_color)
        fill = fill_color != _BRANCO
        for val, larg in zip(valores, larguras):
            pdf.cell(larg, 7, val, border=1, fill=fill,
                     new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.ln()
