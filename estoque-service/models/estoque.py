"""
Modelo ORM para a tabela 'estoque' no banco db_estoque.

Controla a quantidade disponível de cada produto em inventário.
Cada registro vincula um produto_id (do Catálogo Service) à sua quantidade.
O Pedidos Service consulta e decrementa o estoque durante o fluxo de compra.

Regras de negócio:
    - produto_id é único (1 registro por produto)
    - Decremento atômico: verifica quantidade antes de subtrair
    - Produto deve existir no Catálogo antes de receber estoque
"""

from sqlalchemy import Column, Integer, DateTime
from configs.database import Base
from datetime import datetime


class Estoque(Base):
    """
    Entidade Estoque — mapeada para a tabela 'estoque'.

    Campos:
        id                     – Chave primária auto-incrementada
        produto_id             – ID do produto (único, indexado para busca rápida)
        quantidade_disponivel  – Unidades disponíveis em estoque (default: 0)
        atualizado_em          – Última atualização (auto-atualizado pelo onupdate)
    """
    __tablename__ = "estoque"

    id = Column(Integer, primary_key=True, index=True)                              # PK auto-incrementada
    produto_id = Column(Integer, unique=True, nullable=False, index=True)            # FK lógica → Catálogo Service (único por produto)
    quantidade_disponivel = Column(Integer, default=0)                               # Qtd disponível em estoque
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Última atualização