"""
Modelo ORM para a tabela 'pagamentos' no banco db_pagamento.

Registra cada tentativa de pagamento com resultado da simulação.
A processadora simula aprovação com taxa de 85%.
O Pedidos Service chama POST /payments para processar o pagamento do pedido.

Fluxo de status:
    PENDENTE → APROVADO  (simulação aprovou — gera transacao_id)
    PENDENTE → RECUSADO  (simulação recusou — sem transacao_id)
"""

from sqlalchemy import Column, Integer, Float, String, Enum as SQLEnum, DateTime
from configs.database import Base
from datetime import datetime
import enum


class StatusPagamento(str, enum.Enum):
    """
    Enum dos possíveis estados de um pagamento.

    Valores:
        PENDENTE  – Pagamento criado, aguardando processamento
        APROVADO  – Pagamento aprovado pela processadora simulada
        RECUSADO  – Pagamento recusado pela processadora simulada
    """
    PENDENTE = "PENDENTE"
    APROVADO = "APROVADO"
    RECUSADO = "RECUSADO"


class Pagamento(Base):
    """
    Entidade Pagamento — mapeada para a tabela 'pagamentos'.

    Campos:
        id                – Chave primária auto-incrementada
        pedido_id         – ID do pedido associado (FK lógica → Pedidos Service)
        usuario_id        – ID do usuário que fez o pagamento
        valor             – Valor total do pagamento (R$)
        metodo_pagamento  – Método usado (ex: 'PIX', 'CARTAO_CREDITO', 'BOLETO')
        status            – Resultado da simulação (Enum StatusPagamento)
        transacao_id      – ID único da transação (gerado apenas se APROVADO)
        criado_em         – Data/hora do processamento (UTC)
    """
    __tablename__ = "pagamentos"

    id = Column(Integer, primary_key=True, index=True)                              # PK auto-incrementada
    pedido_id = Column(Integer, nullable=False)                                      # FK lógica → Pedidos Service
    usuario_id = Column(Integer, nullable=False)                                     # ID do usuário pagante
    valor = Column(Float, nullable=False)                                            # Valor do pagamento (R$)
    metodo_pagamento = Column(String(20), nullable=False)                             # Método: PIX, CARTAO, BOLETO
    status = Column(SQLEnum(StatusPagamento), default=StatusPagamento.PENDENTE)       # Status da simulação (Enum)
    transacao_id = Column(String(100), nullable=True)                                # ID transação (só se APROVADO)
    criado_em = Column(DateTime, default=datetime.utcnow)                            # Timestamp de criação