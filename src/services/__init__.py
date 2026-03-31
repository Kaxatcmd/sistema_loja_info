"""
Serviços de negócio (pacote).

Exporta:
    - StockService     — monitorização de stock baixo
    - RelatorioService — geração de relatórios em PDF
"""

from src.services.stock_service import StockService
from src.services.relatorio_service import RelatorioService

__all__ = ["StockService", "RelatorioService"]
