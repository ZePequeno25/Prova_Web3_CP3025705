"""
DTOs (Data Transfer Objects) para o Catálogo Service.

Definem os contratos de entrada e saída da API REST.
Usam Pydantic para validação automática de dados:
    - ProdutoCreate  → Dados obrigatórios para criar um produto (entrada)
    - ProdutoResponse → Dados retornados ao cliente após criação/consulta (saída)
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ProdutoCreate(BaseModel):
    """
    DTO de entrada para criação de produto.

    Campos:
        nome      – Nome do produto (obrigatório, deve ser único)
        descricao – Descrição opcional do produto
        preco     – Preço unitário em R$ (obrigatório)

    Exemplo JSON:
        {"nome": "Notebook", "descricao": "Dell Inspiron 15", "preco": 3500.00}
    """
    nome: str
    descricao: Optional[str] = None
    preco: float


class ProdutoResponse(BaseModel):
    """
    DTO de saída para resposta da API.

    Retorna todos os campos do produto, incluindo os gerados automaticamente
    pelo banco de dados (id, ativo, criado_em).

    Campos:
        id        – ID gerado pelo banco (auto-increment)
        nome      – Nome do produto
        descricao – Descrição do produto (pode ser null)
        preco     – Preço unitário em R$
        ativo     – Status de ativação (True/False)
        criado_em – Data/hora de criação (UTC)
    """
    id: int
    nome: str
    descricao: Optional[str]
    preco: float
    ativo: bool
    criado_em: datetime

    class Config:
        # Permite converter objetos SQLAlchemy diretamente para DTO
        from_attributes = True