"""
Modelos ORM para as tabelas 'pedidos' e 'itens_pedido' no banco db_pedidos.

Representa o pedido de compra e seus itens individuais.
O Pedido é a entidade central do sistema — orquestra chamadas para
Usuários, Catálogo, Estoque e Pagamento.

Fluxo de status:
    PENDENTE → PAGO      (pagamento aprovado)
    PENDENTE → CANCELADO  (pagamento recusado ou erro no fluxo)
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum
from configs.database import Base
from datetime import datetime
import enum


class StatusPedido(str, enum.Enum):
    """
    Enum dos possíveis estados de um pedido.

    Valores:
        PENDENTE   – Pedido criado, aguardando pagamento
        PAGO       – Pagamento aprovado pela processadora
        CONFIRMADO – Pedido confirmado (uso futuro)
        CANCELADO  – Pagamento recusado ou erro no processamento
    """
    PENDENTE = "PENDENTE"
    PAGO = "PAGO"
    CONFIRMADO = "CONFIRMADO"
    CANCELADO = "CANCELADO"


class Pedido(Base):
    """
    Entidade Pedido — mapeada para a tabela 'pedidos'.

    Campos:
        id             – Chave primária auto-incrementada
        usuario_id     – ID do usuário (validado via REST no Usuarios Service)
        status         – Estado atual do pedido (Enum StatusPedido)
        valor_total    – Soma dos subtotais de todos os itens (R$)
        criado_em      – Data/hora de criação (UTC)
        atualizado_em  – Última atualização (auto-atualizado pelo onupdate)
    """
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)                              # PK auto-incrementada
    usuario_id = Column(Integer, nullable=False)                                     # FK lógica → Usuarios Service
    status = Column(SQLEnum(StatusPedido), default=StatusPedido.PENDENTE)             # Status do pedido (Enum)
    valor_total = Column(Float, default=0.0)                                         # Valor total calculado (R$)
    criado_em = Column(DateTime, default=datetime.utcnow)                            # Timestamp de criação
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Última atualização


class ItemPedido(Base):
    """
    Entidade ItemPedido — mapeada para a tabela 'itens_pedido'.

    Cada item representa um produto dentro de um pedido com sua quantidade e preço.
    O subtotal é calculado como: quantidade × preco_unitario.

    Campos:
        id              – Chave primária auto-incrementada
        pedido_id       – FK lógica → tabela pedidos
        produto_id      – ID do produto (obtido do Catálogo Service)
        nome_produto    – Nome do produto (copiado no momento da compra)
        quantidade      – Quantidade solicitada
        preco_unitario  – Preço unitário no momento da compra (R$)
        subtotal        – quantidade × preco_unitario (R$)
    """
    __tablename__ = "itens_pedido"

    id = Column(Integer, primary_key=True, index=True)              # PK auto-incrementada
    pedido_id = Column(Integer, nullable=False)                      # FK lógica → pedidos.id
    produto_id = Column(Integer, nullable=False)                     # FK lógica → Catálogo Service
    nome_produto = Column(String(150), nullable=False)               # Nome copiado do catálogo
    quantidade = Column(Integer, nullable=False)                     # Quantidade comprada
    preco_unitario = Column(Float, nullable=False)                   # Preço unitário na data da compra
    subtotal = Column(Float, nullable=False)                         # quantidade × preco_unitario