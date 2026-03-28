"""
DTOs (Data Transfer Objects) para o Pedidos Service.

Definem os contratos de entrada e saída da API REST.
O pedido é a entidade mais complexa — contém uma lista de itens aninhados.

DTOs:
    - ItemPedidoCreate    → Item individual na criação do pedido (entrada)
    - ItemPedidoResponse  → Item com detalhes completos (saída)
    - PedidoCreate        → Pedido com lista de itens (entrada)
    - PedidoResponse      → Pedido completo com status e itens (saída)
"""

from pydantic import BaseModel
from typing import List
from datetime import datetime


class ItemPedidoCreate(BaseModel):
    """
    DTO de entrada para um item do pedido.

    Campos:
        produto_id  – ID do produto no Catálogo Service
        quantidade  – Quantidade desejada (é validada contra o estoque)

    Exemplo JSON:
        {"produto_id": 1, "quantidade": 2}
    """
    produto_id: int
    quantidade: int


class ItemPedidoResponse(BaseModel):
    """
    DTO de saída para um item do pedido.

    Inclui dados obtidos do Catálogo Service (nome, preço) e cálculo do subtotal.

    Campos:
        produto_id      – ID do produto
        nome_produto    – Nome do produto (copiado do Catálogo no momento da compra)
        quantidade      – Quantidade comprada
        preco_unitario  – Preço unitário no momento da compra (R$)
        subtotal        – quantidade × preco_unitario (R$)
    """
    produto_id: int
    nome_produto: str
    quantidade: int
    preco_unitario: float
    subtotal: float


class PedidoCreate(BaseModel):
    """
    DTO de entrada para criação de pedido.

    Campos:
        usuario_id – ID do usuário (validado via REST no Usuarios Service)
        itens      – Lista de itens do pedido (mínimo 1 item)

    Exemplo JSON:
        {
            "usuario_id": 1,
            "itens": [
                {"produto_id": 1, "quantidade": 2},
                {"produto_id": 3, "quantidade": 1}
            ]
        }
    """
    usuario_id: int
    itens: List[ItemPedidoCreate]   # Lista tipada de itens


class PedidoResponse(BaseModel):
    """
    DTO de saída para resposta completa do pedido.

    Retorna pedido com todos os itens e status final.

    Campos:
        id          – ID do pedido (auto-increment)
        usuario_id  – ID do usuário dono do pedido
        status      – Status atual: 'PENDENTE', 'PAGO' ou 'CANCELADO'
        valor_total – Soma de todos os subtotais dos itens (R$)
        criado_em   – Data/hora de criação (UTC)
        itens       – Lista de itens com detalhes completos
    """
    id: int
    usuario_id: int
    status: str
    valor_total: float
    criado_em: datetime
    itens: List[ItemPedidoResponse]

    class Config:
        # Permite converter objetos SQLAlchemy diretamente para DTO
        from_attributes = True