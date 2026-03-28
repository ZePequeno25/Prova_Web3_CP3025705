"""
Modelo ORM para a tabela 'produtos' no banco db_catalogo.

Representa um produto no catálogo da loja.
Cada produto possui nome único, descrição opcional, preço e status ativo/inativo.
Este modelo é consultado pelo Pedidos Service (via REST) para obter preço unitário.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from configs.database import Base
from datetime import datetime


class Produto(Base):
    """
    Entidade Produto — mapeada para a tabela 'produtos'.

    Campos:
        id            – Chave primária auto-incrementada
        nome          – Nome do produto (único, máx. 150 caracteres)
        descricao     – Descrição opcional (máx. 500 caracteres)
        preco         – Preço unitário em R$ (obrigatório)
        ativo         – Flag de ativação (default: True)
        criado_em     – Data/hora de criação automática (UTC)
    """
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)              # PK auto-incrementada
    nome = Column(String(150), nullable=False, unique=True)         # Nome único do produto
    descricao = Column(String(500))                                  # Descrição opcional
    preco = Column(Float, nullable=False)                            # Preço unitário em R$
    ativo = Column(Boolean, default=True)                            # Produto ativo/inativo
    criado_em = Column(DateTime, default=datetime.utcnow)            # Timestamp de criação 