"""
DTOs (Data Transfer Objects) para o Pagamento Service.

Definem os contratos de entrada e saída da API REST.
    - PagamentoCreate   → Dados necessários para processar pagamento (entrada)
    - PagamentoResponse  → Resultado do processamento com status (saída)

O Pedidos Service envia POST /payments com PagamentoCreate e
recebe PagamentoResponse com status APROVADO ou RECUSADO.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PagamentoCreate(BaseModel):
    """
    DTO de entrada para processamento de pagamento.

    Campos:
        pedido_id         – ID do pedido a ser pago
        usuario_id        – ID do usuário pagante
        valor             – Valor total a ser cobrado (R$)
        metodo_pagamento  – Método: 'PIX', 'CARTAO_CREDITO', 'BOLETO', etc.

    Exemplo JSON:
        {
            "pedido_id": 1,
            "usuario_id": 1,
            "valor": 7000.00,
            "metodo_pagamento": "PIX"
        }
    """
    pedido_id: int
    usuario_id: int
    valor: float
    metodo_pagamento: str              # Método de pagamento escolhido


class PagamentoResponse(BaseModel):
    """
    DTO de saída com resultado do pagamento.

    O status é retornado como string (não Enum) para compatibilidade JSON.
    O transacao_id só é gerado quando o pagamento é APROVADO.

    Campos:
        id                – ID do pagamento no banco
        pedido_id         – ID do pedido associado
        usuario_id        – ID do usuário pagante
        valor             – Valor cobrado (R$)
        metodo_pagamento  – Método utilizado
        status            – 'APROVADO' ou 'RECUSADO' (string)
        transacao_id      – ID único da transação (None se RECUSADO)
        criado_em         – Data/hora do processamento (UTC)
    """
    id: int
    pedido_id: int
    usuario_id: int
    valor: float
    metodo_pagamento: str
    status: str                        # String (convertido do Enum no Service)
    transacao_id: Optional[str]        # Apenas preenchido se APROVADO
    criado_em: datetime

    class Config:
        # Permite converter objetos SQLAlchemy diretamente para DTO
        from_attributes = True