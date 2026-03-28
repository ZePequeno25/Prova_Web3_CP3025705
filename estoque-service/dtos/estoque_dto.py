"""
DTOs (Data Transfer Objects) para o Estoque Service.

Definem os contratos de entrada e saída da API REST.
    - EstoqueCreate   → Dados para criar/atualizar estoque de um produto (entrada)
    - EstoqueResponse  → Dados retornados com quantidade disponível (saída)

O Pedidos Service usa o EstoqueResponse para validar disponibilidade
antes de processar um pedido.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class EstoqueCreate(BaseModel):
    """
    DTO de entrada para criação/atualização de estoque.

    Campos:
        produto_id             – ID do produto no Catálogo Service (obrigatório)
        quantidade_disponivel  – Quantidade inicial em estoque (default: 0)

    Exemplo JSON:
        {"produto_id": 1, "quantidade_disponivel": 50}
    """
    produto_id: int
    quantidade_disponivel: int = 0     # Quantidade inicial (padrão: 0)


class EstoqueResponse(BaseModel):
    """
    DTO de saída para consulta de estoque.

    Retorna a quantidade disponível atual e a última atualização.

    Campos:
        produto_id             – ID do produto consultado
        quantidade_disponivel  – Unidades disponíveis em estoque
        atualizado_em          – Data/hora da última atualização (UTC)
    """
    produto_id: int
    quantidade_disponivel: int
    atualizado_em: datetime

    class Config:
        # Permite converter objetos SQLAlchemy diretamente para DTO
        from_attributes = True